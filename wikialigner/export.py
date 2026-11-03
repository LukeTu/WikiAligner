"""Write an alignment result to Excel, CSV or JSON, with provenance and licence notes."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill

FORMATS = ("xlsx", "csv", "json")

_REASONS = {"weak": "below threshold", "taken": "best counterpart paired elsewhere"}


def _doc_label(doc: dict) -> str:
    rev = doc.get("revision")
    if rev:
        return f"{doc['title']} ({doc['lang']}, rev {rev['revid']}, {rev['timestamp'][:10]})"
    return f"{doc['title']} ({doc['lang']})"


def default_filename(result: dict, fmt: str) -> str:
    def part(doc):
        rev = doc.get("revision")
        return f"{doc['title']}_{doc['lang']}" + (f"_{rev['revid']}" if rev else "")
    name = f"{part(result['left'])}__{part(result['right'])}"
    name = re.sub(r'[\\/:*?"<>|\s]+', "_", name)[:150]
    return f"{name}.{fmt}"


def pair_rows(result: dict) -> list[dict]:
    s1, s2 = result["left"]["segments"], result["right"]["segments"]
    rows = []
    for p in result["pairs"]:
        a, b = s1[p["src"]], s2[p["tgt"]]
        rows.append({
            "left_id": a["id"], "left_section": a["section"], "left_text": a["text"],
            "right_id": b["id"], "right_section": b["section"], "right_text": b["text"],
            "cosine": p["cos"], "margin": p["margin"], "char_ratio": p.get("char_ratio"), "type": p["kind"],
        })
    return rows


def unmatched_rows(result: dict, side: str) -> list[dict]:
    segs = result[side]["segments"]
    key = "unmatched_src" if side == "left" else "unmatched_tgt"
    return [{"id": u["id"], "section": segs[u["id"]]["section"], "text": segs[u["id"]]["text"],
             "best_counterpart": u["best"], "best_margin": u["margin"], "reason": _REASONS.get(u["reason"], u["reason"])}
            for u in result[key]]


def metadata_rows(result: dict) -> list[tuple[str, str]]:
    rows = [
        ("Created", result["created"]),
        ("WikiAligner version", result["app_version"]),
        ("Mode", result["mode"]),
        ("Left", _doc_label(result["left"])),
        ("Left URL", result["left"].get("url", "")),
        ("Right", _doc_label(result["right"])),
        ("Right URL", result["right"].get("url", "")),
        ("Model", result["model"]["id"]),
    ]
    rows += [(f"Option: {k}", str(v)) for k, v in result["options"].items()]
    rows += [(f"Stat: {k}", str(v)) for k, v in result["stats"].items()]
    if result["left"]["source"] == "wiki" or result["right"]["source"] == "wiki":
        rows.append(("Licence", "Text from Wikipedia, available under CC BY-SA 4.0 "
                                "(https://creativecommons.org/licenses/by-sa/4.0/). "
                                "Credit the article URLs above when reusing it."))
    return rows


def export(result: dict, fmt: str, directory: Path) -> Path:
    if fmt not in FORMATS:
        raise ValueError(f"format must be one of {FORMATS}")
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / default_filename(result, fmt)
    stem, n = path.stem, 1
    while path.exists():
        path = directory / f"{stem} ({n}).{fmt}"
        n += 1

    if fmt == "json":
        path.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    elif fmt == "csv":
        rows = pair_rows(result)
        with path.open("w", newline="", encoding="utf-8-sig") as f:  # BOM so Excel reads UTF-8
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ["left_text", "right_text"])
            w.writeheader()
            w.writerows(rows)
    else:
        _write_xlsx(result, path)
    return path


def _write_xlsx(result: dict, path: Path) -> None:
    wb = Workbook()
    head_font = Font(bold=True, color="FFFFFF")
    head_fill = PatternFill("solid", fgColor="0D6A61")
    wrap = Alignment(wrap_text=True, vertical="top")

    def sheet(ws, rows: list[dict], widths: dict[str, int]):
        if not rows:
            ws.append(["(none)"])
            return
        cols = list(rows[0].keys())
        ws.append(cols)
        for c in ws[1]:
            c.font, c.fill = head_font, head_fill
        for r in rows:
            ws.append([r[c] for c in cols])
        for i, col in enumerate(cols, start=1):
            letter = ws.cell(row=1, column=i).column_letter
            ws.column_dimensions[letter].width = widths.get(col, 12)
        for row in ws.iter_rows(min_row=2):
            for c in row:
                c.alignment = wrap
        ws.freeze_panes = "A2"

    ws = wb.active
    ws.title = "Aligned pairs"
    sheet(ws, pair_rows(result), {"left_text": 60, "right_text": 60, "left_section": 18, "right_section": 18})
    sheet(wb.create_sheet("Unmatched left"), unmatched_rows(result, "left"), {"text": 80, "section": 20, "reason": 30})
    sheet(wb.create_sheet("Unmatched right"), unmatched_rows(result, "right"), {"text": 80, "section": 20, "reason": 30})
    meta = wb.create_sheet("About")
    for k, v in metadata_rows(result):
        meta.append([k, v])
    meta.column_dimensions["A"].width = 24
    meta.column_dimensions["B"].width = 100
    wb.save(path)
