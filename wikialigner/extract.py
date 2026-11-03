"""Turn rendered Wikipedia HTML into ordered text blocks.

Works on both the legacy parser output and Parsoid output that ``action=render`` returns.
Unlike the TextExtracts plain-text API used by the first version, this keeps section
structure, list items and image captions, and can optionally keep infoboxes and tables.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from bs4 import BeautifulSoup, NavigableString, Tag

# Elements that never carry article prose.
_REMOVE = [
    "style", "script", "link", "meta", "noscript",
    "sup.reference", "sup.mw-ref", "sup.noprint", "span.mw-editsection", ".mw-cite-backlink",
    ".reflist", "ol.references", ".mw-references-wrap", ".navbox", ".navbox-styles", ".vertical-navbox",
    ".metadata", ".ambox", ".mbox-small", ".noprint", ".mw-empty-elt", ".toc", "#toc", ".shortdescription",
    ".mw-jump-link", ".catlinks", ".printfooter", ".portalbox", ".sistersitebox", ".hatnote",
    ".mwe-math-mathml-inline", ".mwe-math-mathml-display", ".sidebar", ".navbar", "table.sidebar",
    ".authority-control", ".side-box", ".plainlinks.hlist", "span.Z3988",
    # Template and parser error messages, e.g. a maintenance template used with a missing parameter.
    "span.error", "strong.error", "div.error", "p.error", ".scribunto-error",
]

# Level-2 section titles after which content is reference apparatus, in common languages.
APPENDIX_TITLES = {
    # en
    "references", "external links", "see also", "notes", "further reading", "bibliography", "sources",
    "citations", "footnotes", "notes and references", "works cited", "explanatory notes",
    # zh
    "参考文献", "參考文獻", "参考资料", "參考資料", "外部链接", "外部連結", "參見", "参见", "参阅", "參閱",
    "注释", "註釋", "注釋", "延伸阅读", "延伸閱讀", "相关条目", "相關條目", "脚注", "腳註", "来源", "來源",
    # ja
    "出典", "関連項目", "外部リンク", "注釈",
    # ko
    "각주", "외부 링크", "같이 보기", "참고 문헌",
    # ru / uk
    "примечания", "ссылки", "см. также", "литература", "источники", "примітки", "посилання", "див. також",
    "джерела", "література",
    # de
    "einzelnachweise", "weblinks", "siehe auch", "literatur", "anmerkungen", "quellen",
    # fr
    "notes et références", "liens externes", "voir aussi", "bibliographie", "références",
    # es / pt / it
    "referencias", "enlaces externos", "véase también", "bibliografía", "notas", "referências",
    "ligações externas", "ver também", "bibliografia", "note", "collegamenti esterni", "voci correlate",
    # ar
    "مراجع", "وصلات خارجية", "انظر أيضا", "انظر أيضًا", "المراجع",
}

_WS = re.compile(r"\s+")


@dataclass
class Block:
    kind: str      # heading | paragraph | list | caption | quote | table | infobox
    text: str
    section: str   # heading path, e.g. "Investigation / Suspects"
    level: int = 0  # heading level for headings


def _clean_text(el: Tag) -> str:
    return _WS.sub(" ", el.get_text("")).strip()


def _own_text(el: Tag, skip=("ul", "ol", "dl")) -> str:
    """Text of ``el`` without nested lists, which are emitted as blocks of their own."""
    parts = []
    for child in el.children:
        if isinstance(child, NavigableString):
            parts.append(str(child))
        elif isinstance(child, Tag) and child.name not in skip:
            parts.append(child.get_text(""))
    return _WS.sub(" ", "".join(parts)).strip()


def _heading_level(el: Tag) -> int:
    return int(el.name[1]) if el.name in ("h1", "h2", "h3", "h4", "h5", "h6") else 0


def extract_blocks(html: str, *, include_captions: bool = True, include_lists: bool = True,
                   include_tables: bool = False, include_infobox: bool = False,
                   include_appendix: bool = False) -> list[Block]:
    soup = BeautifulSoup(html, "lxml")
    root = soup.select_one(".mw-parser-output") or soup.body or soup

    for sel in _REMOVE:
        for el in root.select(sel):
            el.decompose()
    for br in root.find_all("br"):
        br.replace_with(" ")

    blocks: list[Block] = []

    # Infobox and data tables are pulled out first so their cells do not leak in as paragraphs.
    for table in root.find_all("table"):
        if table.parent is None:
            continue  # already removed with an enclosing table
        classes = set(table.get("class") or [])
        is_infobox = bool({"infobox", "infobox_v2", "infobox_v3"} & classes) or any(
            c.startswith("infobox") for c in classes)
        wanted = include_infobox if is_infobox else include_tables
        if wanted:
            for row in table.find_all("tr"):
                cells = [_clean_text(c) for c in row.find_all(["th", "td"], recursive=False)]
                cells = [c for c in cells if c]
                if cells:
                    blocks.append(Block("infobox" if is_infobox else "table", " | ".join(cells), ""))
        table.decompose()

    section_path: list[str] = []
    skipping = False
    for el in root.find_all(True):
        if el.parent is None:
            continue
        name = el.name
        level = _heading_level(el)
        if level:
            title = _clean_text(el)
            if not title:
                continue
            if level <= 2:
                skipping = (not include_appendix) and title.casefold().rstrip(":：") in APPENDIX_TITLES
            del section_path[max(level - 2, 0):]
            section_path.append(title)
            if not skipping:
                blocks.append(Block("heading", title, " / ".join(section_path[:-1]), level))
            continue
        if skipping:
            continue

        section = " / ".join(section_path)
        if name == "p":
            if el.find_parent(["li", "figcaption", "dd"]) is not None:
                continue
            text = _clean_text(el)
            if text:
                kind = "quote" if el.find_parent("blockquote") is not None else "paragraph"
                blocks.append(Block(kind, text, section))
        elif name == "li" and include_lists:
            if el.find_parent(["figcaption"]) is not None:
                continue
            classes = el.get("class") or []
            if "gallerybox" in classes:
                if include_captions:
                    cap = el.select_one(".gallerytext")
                    text = _clean_text(cap) if cap else ""
                    if text:
                        blocks.append(Block("caption", text, section))
                continue
            text = _own_text(el)
            if text:
                blocks.append(Block("list", text, section))
        elif name == "dd":
            text = _own_text(el)
            if text:
                blocks.append(Block("paragraph", text, section))
        elif name == "blockquote" and el.find("p") is None:
            text = _clean_text(el)
            if text:
                blocks.append(Block("quote", text, section))
        elif include_captions and (name == "figcaption" or "thumbcaption" in (el.get("class") or [])):
            text = _clean_text(el)
            if text:
                blocks.append(Block("caption", text, section))
    return blocks


def blocks_from_plain_text(text: str) -> list[Block]:
    """Blocks for user-supplied text: blank lines separate paragraphs."""
    paragraphs = re.split(r"\n\s*\n", text.replace("\r\n", "\n"))
    blocks = []
    for para in paragraphs:
        lines = [l.strip() for l in para.split("\n") if l.strip()]
        if not lines:
            continue
        # Markdown-style headings are kept as headings so long documents stay navigable.
        if len(lines) == 1 and lines[0].startswith("#"):
            blocks.append(Block("heading", lines[0].lstrip("#").strip(), "", 2))
        else:
            blocks.append(Block("paragraph", " ".join(lines), ""))
    return blocks
