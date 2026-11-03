"""Revision-history features: finding when a sentence first appeared in an article.

The search works like WikiBlame: it bisects the revision list, so it needs about
log2(number of revisions) page fetches. Like WikiBlame it assumes that once a sentence
appears it stays; if it was removed and re-added later, the result is one of the times
it appeared, not necessarily the first.
"""
from __future__ import annotations

import difflib
import re
from typing import Callable

from .extract import extract_blocks
from .segment import split_sentences
from .wiki import Revision, WikiClient, WikiError, diff_url, page_url

# Tags that MediaWiki adds to edits made with the Content Translation tool.
CONTENT_TRANSLATION_TAGS = {"contenttranslation", "contenttranslation-v2", "sectiontranslation"}

_WS = re.compile(r"\s+")


def _norm(text: str) -> str:
    return _WS.sub(" ", text).strip().casefold()


def is_content_translation(rev: Revision) -> bool:
    return bool(CONTENT_TRANSLATION_TAGS & set(rev.tags))


class _Probe:
    """Fetches one revision and answers whether it contains the target text."""

    def __init__(self, client: WikiClient, lang: str, variant: str | None, needle: str, fuzzy: float | None):
        self.client, self.lang, self.variant = client, lang, variant
        self.needle = _norm(needle)
        self.fuzzy = fuzzy
        self.fetches = 0

    def __call__(self, rev: Revision) -> tuple[bool, float]:
        self.fetches += 1
        html = self.client.fetch_html(self.lang, rev.revid, self.variant)
        blocks = extract_blocks(html, include_tables=True, include_infobox=True, include_appendix=True)
        full = _norm(" ".join(b.text for b in blocks))
        if self.needle in full:
            return True, 1.0
        if self.fuzzy is None:
            return False, 0.0
        best = 0.0
        for b in blocks:
            for sent in split_sentences(b.text, self.lang):
                cand = _norm(sent)
                sm = difflib.SequenceMatcher(None, self.needle, cand)
                if sm.real_quick_ratio() < self.fuzzy or sm.quick_ratio() < self.fuzzy:
                    continue
                best = max(best, sm.ratio())
                if best >= self.fuzzy:
                    return True, best
        return False, best


def trace_first_appearance(client: WikiClient, lang: str, title: str, text: str, until_revid: int,
                           variant: str | None = None, fuzzy: float | None = None,
                           progress: Callable[[str], None] = lambda s: None) -> dict:
    """Earliest revision (up to ``until_revid``) whose text contains ``text``.

    ``fuzzy`` (0–1) accepts near-identical sentences, so later typo fixes do not hide
    the original insertion; ``None`` requires the exact sentence.
    """
    progress("list_revisions")
    revs = list(client.iter_revisions(lang, title, until_revid=until_revid,
                                      progress=lambda n: progress(f"list_revisions {n}")))
    if not revs or revs[-1].revid != until_revid:
        raise WikiError(f"Revision {until_revid} is not in the history of {title!r}")

    probe = _Probe(client, lang, variant, text, fuzzy)
    present, score = probe(revs[-1])
    if not present:
        raise WikiError("The sentence was not found in the chosen revision; try fuzzy matching")

    lo, hi = 0, len(revs) - 1
    best_score = score
    while lo < hi:
        mid = (lo + hi) // 2
        progress(f"probe {probe.fetches} {revs[mid].timestamp[:10]}")
        found, s = probe(revs[mid])
        if found:
            hi, best_score = mid, s
        else:
            lo = mid + 1

    rev = revs[lo]
    previous = revs[lo - 1] if lo > 0 else None
    return {
        "lang": lang,
        "title": title,
        "text": text,
        "revision": rev.to_dict(),
        "previous": previous.to_dict() if previous else None,
        "is_page_creation": lo == 0,
        "content_translation": is_content_translation(rev),
        "match_score": round(best_score, 3),
        "fuzzy": fuzzy,
        "revisions_searched": len(revs),
        "fetches": probe.fetches,
        "url": page_url(lang, title, rev.revid),
        "diff_url": diff_url(lang, rev.revid),
    }


def compare_traces(a: dict, b: dict) -> dict:
    """Which of two traced sentences appeared first, as evidence for translation direction."""
    ta, tb = a["revision"]["timestamp"], b["revision"]["timestamp"]
    if ta == tb:
        earlier = None
    else:
        earlier = "left" if ta < tb else "right"
    return {
        "earlier": earlier,
        "left_timestamp": ta,
        "right_timestamp": tb,
        "content_translation_left": a.get("content_translation", False),
        "content_translation_right": b.get("content_translation", False),
    }
