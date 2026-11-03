"""From two source specifications to one alignment result."""
from __future__ import annotations

import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Callable

from . import __version__
from .align import AlignParams, align_documents
from .extract import Block, blocks_from_plain_text, extract_blocks
from .models import DEFAULT_MODEL, ModelManager, resolve_model_id
from .segment import GRANULARITIES, Segment, segment_blocks
from .wiki import Revision, WikiClient, WikiError, check_lang, page_url

Progress = Callable[[str], None]


@dataclass
class SourceSpec:
    type: str = "wiki"               # wiki | text
    lang: str = "en"
    title: str = ""                  # wiki
    revid: int | None = None         # wiki: exact revision
    date: str | None = None          # wiki: revision current at this date
    variant: str | None = None       # wiki: script variant, e.g. zh-hans
    text: str = ""                   # text
    name: str = ""                   # text: label shown in the UI

    @classmethod
    def from_dict(cls, d: dict) -> "SourceSpec":
        known = set(cls.__dataclass_fields__)
        spec = cls(**{k: v for k, v in d.items() if k in known})
        if spec.revid in ("", 0):
            spec.revid = None
        if spec.revid is not None:
            spec.revid = int(spec.revid)
        spec.date = spec.date or None
        spec.variant = spec.variant or None
        return spec


@dataclass
class AlignOptions:
    model: str = DEFAULT_MODEL
    granularity: str = "sentence"
    strategy: str = "greedy"
    k: int = 4
    min_margin: float = 1.0
    include_captions: bool = True
    include_lists: bool = True
    include_tables: bool = False
    include_infobox: bool = False
    align_headings: bool = False
    exact_first: bool | None = None  # None: on when both sides share a language

    @classmethod
    def from_dict(cls, d: dict | None) -> "AlignOptions":
        known = set(cls.__dataclass_fields__)
        opts = cls(**{k: v for k, v in (d or {}).items() if k in known})
        if opts.granularity not in GRANULARITIES:
            raise ValueError(f"Unknown granularity {opts.granularity!r}")
        opts.k = max(1, min(int(opts.k), 16))
        opts.min_margin = float(opts.min_margin)
        return opts

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Document:
    source: str
    lang: str
    title: str
    segments: list[Segment]
    revision: Revision | None = None
    variant: str | None = None
    url: str = ""
    blocks: int = 0
    extra: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "lang": self.lang,
            "title": self.title,
            "revision": self.revision.to_dict() if self.revision else None,
            "variant": self.variant,
            "url": self.url,
            "blocks": self.blocks,
            "segments": [s.to_dict() for s in self.segments],
            **self.extra,
        }


def resolve_revision(client: WikiClient, spec: SourceSpec) -> tuple[str, Revision]:
    """Canonical title and the revision a spec points at (exact id, as-of date, or latest)."""
    if spec.revid:
        return client.revision_by_id(spec.lang, spec.revid)
    info = client.page_info(spec.lang, spec.title)
    if spec.date:
        return info.title, client.revision_at(spec.lang, info.title, spec.date)
    return client.revision_by_id(spec.lang, info.lastrevid)


def wiki_blocks(client: WikiClient, lang: str, revid: int, variant: str | None, opts: AlignOptions) -> list[Block]:
    html = client.fetch_html(lang, revid, variant)
    return extract_blocks(html, include_captions=opts.include_captions, include_lists=opts.include_lists,
                          include_tables=opts.include_tables, include_infobox=opts.include_infobox)


def load_document(spec: SourceSpec, client: WikiClient, opts: AlignOptions) -> Document:
    lang = check_lang(spec.lang)
    if spec.type == "text":
        blocks = blocks_from_plain_text(spec.text)
        segments = segment_blocks(blocks, lang, opts.granularity, opts.align_headings)
        return Document("text", lang, spec.name or "Text", segments, blocks=len(blocks))
    if not spec.title and not spec.revid:
        raise WikiError("Choose an article title")
    title, rev = resolve_revision(client, spec)
    blocks = wiki_blocks(client, lang, rev.revid, spec.variant, opts)
    segments = segment_blocks(blocks, lang, opts.granularity, opts.align_headings)
    return Document("wiki", lang, title, segments, revision=rev, variant=spec.variant,
                    url=page_url(lang, title, rev.revid), blocks=len(blocks),
                    extra={"requested": {"revid": spec.revid, "date": spec.date}})


def run_alignment(left: SourceSpec, right: SourceSpec, opts: AlignOptions, client: WikiClient,
                  models: ModelManager, progress: Progress = lambda s: None) -> dict:
    started = time.time()
    progress("fetch_left")
    doc1 = load_document(left, client, opts)
    progress("fetch_right")
    doc2 = load_document(right, client, opts)
    if not any(s.alignable for s in doc1.segments) or not any(s.alignable for s in doc2.segments):
        raise WikiError("One of the two texts has no sentences to align")

    embedder = models.get(opts.model, progress)
    progress("embed")
    texts1 = [s.text for s in doc1.segments]
    texts2 = [s.text for s in doc2.segments]
    emb1 = embedder.encode(texts1)
    emb2 = embedder.encode(texts2)

    progress("align")
    same_language = doc1.lang == doc2.lang
    exact_first = opts.exact_first if opts.exact_first is not None else same_language
    params = AlignParams(k=opts.k, min_margin=opts.min_margin, strategy=opts.strategy, exact_first=exact_first)
    result = align_documents(texts1, texts2, emb1, emb2,
                             [s.alignable for s in doc1.segments], [s.alignable for s in doc2.segments],
                             params, same_language=same_language)

    n1 = sum(s.alignable for s in doc1.segments)
    n2 = sum(s.alignable for s in doc2.segments)
    m1 = len({p["src"] for p in result["pairs"]})
    m2 = len({p["tgt"] for p in result["pairs"]})
    return {
        "id": uuid.uuid4().hex[:12],
        "created": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "app_version": __version__,
        "mode": "revision" if same_language else "crosslingual",
        "left": doc1.to_dict(),
        "right": doc2.to_dict(),
        "options": {**opts.to_dict(), "exact_first": exact_first},
        "model": {"id": resolve_model_id(opts.model), "dim": embedder.dim},
        **result,
        "stats": {
            "pairs": len(result["pairs"]),
            "identical": sum(p["kind"] == "identical" for p in result["pairs"]),
            "alignable_src": n1,
            "alignable_tgt": n2,
            "coverage_src": round(m1 / n1, 4) if n1 else 0,
            "coverage_tgt": round(m2 / n2, 4) if n2 else 0,
            "seconds": round(time.time() - started, 1),
        },
    }
