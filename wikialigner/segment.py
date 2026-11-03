"""Sentence and clause segmentation for many scripts.

Segmentation runs per block (paragraph, list item, caption), so lines without final
punctuation never get glued to the next sentence.
"""
from __future__ import annotations

import re
import warnings
from dataclasses import asdict, dataclass
from functools import lru_cache

from .extract import Block

# Scripts where sentences end with full-width punctuation and words are not space-separated.
CJK_LANGS = {"zh", "ja", "yue", "zh-yue", "wuu", "gan", "lzh", "zh-classical"}
# Scripts where spaces mark phrase or sentence boundaries.
SPACE_DELIMITED_LANGS = {"th", "lo"}
# Scripts with their own sentence terminator.
TERMINATOR_LANGS = {"my": "။", "km": "។", "bo": "།", "dz": "།", "si": "෴"}
# Languages with dedicated rules in pysbd; other alphabetic languages use its English rules.
PYSBD_LANGS = {"en", "hi", "mr", "es", "am", "ar", "hy", "bg", "ur", "ru", "pl", "fa", "nl", "da",
               "fr", "el", "it", "de", "kk", "sk"}
# Closest pysbd rule set for related languages, mainly for their abbreviation lists.
PYSBD_FALLBACK = {"pt": "es", "ca": "es", "gl": "es", "ast": "es", "uk": "ru", "be": "ru", "mk": "bg",
                  "sr": "bg", "cs": "sk", "sv": "da", "no": "da", "nb": "da", "nn": "da", "af": "nl",
                  "lb": "de", "ro": "it", "ne": "hi", "sa": "hi", "ps": "fa", "ckb": "fa", "tt": "kk"}

GRANULARITIES = ("sentence", "clause", "paragraph")

_CJK_END = "。！？!?﹖﹗．"
_CLOSE = "」』”’\"）)】〕》"
_CJK_SPLIT = re.compile(
    rf"(?<=[{_CJK_END}])(?=[^{_CLOSE}{_CJK_END}])|(?<=[{_CJK_END}][{_CLOSE}])"
)
_CJK_CLAUSE = re.compile(r"(?<=[，；：﹔;])")
_LATIN_CLAUSE = re.compile(r"(?<=[,;:])\s+|\s+[–—]\s+")


@dataclass
class Segment:
    id: int
    text: str
    kind: str        # block kind: heading | paragraph | list | caption | quote | table | infobox
    section: str
    block: int       # index of the block this segment came from
    alignable: bool  # False for headings (by default) and segments with almost no letters

    def to_dict(self) -> dict:
        return asdict(self)


def base_lang(lang: str) -> str:
    return (lang or "").lower().split("-")[0]


def is_cjk(lang: str) -> bool:
    # Wikipedia codes, so zh-min-nan (written in Latin script) is deliberately not included.
    return lang in CJK_LANGS


@lru_cache(maxsize=None)
def _pysbd(lang: str):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", SyntaxWarning)
        import pysbd
    lang = PYSBD_FALLBACK.get(lang, lang)
    return pysbd.Segmenter(language=lang if lang in PYSBD_LANGS else "en", clean=False)


def split_sentences(text: str, lang: str) -> list[str]:
    text = text.strip()
    if not text:
        return []
    if is_cjk(lang):
        parts = _CJK_SPLIT.split(text)
    elif base_lang(lang) in SPACE_DELIMITED_LANGS:
        parts = _merge_short(re.split(r"\s+", text), 15, joiner=" ")
    elif base_lang(lang) in TERMINATOR_LANGS:
        term = re.escape(TERMINATOR_LANGS[base_lang(lang)])
        parts = re.split(rf"(?<={term})\s*", text)
    else:
        parts = _rejoin_titles(_pysbd(base_lang(lang)).segment(text))
    return [p.strip() for p in parts if p and p.strip()]


# Honorifics that pysbd treats as sentence ends when a capitalised name follows ("Sr. Silva").
_TITLE_END = re.compile(
    r"(?:^|\s)(?:Mr|Mrs|Ms|Dr|Dra|Prof|Profa|St|Sr|Sra|Srta|Sres|Gen|Col|Lt|Capt|Sgt|Rev|Hon|Mt|Ft|Fr|Hr|"
    r"Dott|Sig|Av|Avda|Pres|Gov|Sen|Rep|Mme|Mlle|Mgr|Hl)\.\s*$")


def _rejoin_titles(parts: list[str]) -> list[str]:
    out: list[str] = []
    for p in parts:
        if out and _TITLE_END.search(out[-1]):
            out[-1] = out[-1].rstrip() + " " + p.lstrip()
        else:
            out.append(p)
    return out


def split_clauses(sentence: str, lang: str) -> list[str]:
    if is_cjk(lang):
        parts, min_len, joiner = _CJK_CLAUSE.split(sentence), 6, ""
    else:
        parts, min_len, joiner = _LATIN_CLAUSE.split(sentence), 20, " "
    return _merge_short([p.strip() for p in parts if p and p.strip()], min_len, joiner)


def _merge_short(parts: list[str], min_len: int, joiner: str) -> list[str]:
    """Attach pieces shorter than ``min_len`` to their neighbour so no fragment stands alone."""
    out: list[str] = []
    for p in parts:
        if out and (len(p) < min_len or len(out[-1]) < min_len):
            out[-1] = out[-1] + joiner + p
        else:
            out.append(p)
    return out


def _letters(text: str) -> int:
    return sum(ch.isalpha() for ch in text)


def segment_blocks(blocks: list[Block], lang: str, granularity: str = "sentence",
                   align_headings: bool = False) -> list[Segment]:
    if granularity not in GRANULARITIES:
        raise ValueError(f"granularity must be one of {GRANULARITIES}")
    min_letters = 2 if is_cjk(lang) else 3
    segments: list[Segment] = []
    for b_idx, block in enumerate(blocks):
        if block.kind == "heading" or granularity == "paragraph":
            pieces = [block.text]
        else:
            pieces = split_sentences(block.text, lang)
            if granularity == "clause":
                pieces = [c for s in pieces for c in split_clauses(s, lang)]
        for piece in pieces:
            alignable = _letters(piece) >= min_letters and (block.kind != "heading" or align_headings)
            segments.append(Segment(len(segments), piece, block.kind, block.section, b_idx, alignable))
    return segments
