"""Margin-based sentence matching between two documents.

Scores follow Artetxe & Schwenk (2019): the ratio margin divides the cosine of a pair by
the average cosine of each side's k nearest neighbours, which corrects for "hub" sentences
that are close to everything. The candidate search and greedy one-to-one selection follow
the sentence-transformers bitext-mining example (Apache-2.0), rewritten in vectorised NumPy
so that k never exceeds the number of available sentences.
"""
from __future__ import annotations

import difflib
from dataclasses import asdict, dataclass

import numpy as np

STRATEGIES = ("greedy", "mutual", "many")


@dataclass
class AlignParams:
    k: int = 4
    min_margin: float = 1.0
    strategy: str = "greedy"    # greedy: one-to-one | mutual: both sides agree | many: allow 1-n and n-1
    exact_first: bool = False   # pair identical sentences before scoring (revision comparison)

    def to_dict(self) -> dict:
        return asdict(self)


def normalize(text: str) -> str:
    return " ".join(text.split())


def margin_matrix(e1: np.ndarray, e2: np.ndarray, k: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return (cosine, margin, candidate mask) for row-normalised embeddings."""
    n, m = e1.shape[0], e2.shape[0]
    cos = e1 @ e2.T
    k1, k2 = max(1, min(k, m)), max(1, min(k, n))
    top_rows = np.partition(cos, m - k1, axis=1)[:, m - k1:]   # k1 best per row
    top_cols = np.partition(cos, n - k2, axis=0)[n - k2:, :]   # k2 best per column
    fwd_mean = top_rows.mean(axis=1)
    bwd_mean = top_cols.mean(axis=0)
    denom = (fwd_mean[:, None] + bwd_mean[None, :]) / 2.0
    margin = np.where(denom > 1e-6, cos / np.maximum(denom, 1e-6), 0.0)
    # Only each row's and each column's k nearest neighbours by cosine are candidates.
    row_thresh = top_rows.min(axis=1)[:, None]
    col_thresh = top_cols.min(axis=0)[None, :]
    candidates = (cos >= row_thresh) | (cos >= col_thresh)
    return cos, margin, candidates


def align_embeddings(e1: np.ndarray, e2: np.ndarray, params: AlignParams) -> list[tuple[int, int, float, float]]:
    """Pairs (i, j, cosine, margin) over the rows of e1 and e2."""
    if params.strategy not in STRATEGIES:
        raise ValueError(f"strategy must be one of {STRATEGIES}")
    if len(e1) == 0 or len(e2) == 0:
        return []
    cos, margin, cand = margin_matrix(e1, e2, params.k)
    scored = np.where(cand, margin, -np.inf)
    fwd_best = scored.argmax(axis=1)   # best target for each source
    bwd_best = scored.argmax(axis=0)   # best source for each target

    pairs = {(i, int(fwd_best[i])) for i in range(len(e1))}
    pairs |= {(int(bwd_best[j]), j) for j in range(len(e2))}
    pairs = [(i, j) for i, j in pairs if margin[i, j] >= params.min_margin]
    pairs.sort(key=lambda p: -margin[p])

    if params.strategy == "mutual":
        chosen = [(i, j) for i, j in pairs if fwd_best[i] == j and bwd_best[j] == i]
    elif params.strategy == "many":
        chosen = pairs
    else:
        used1, used2, chosen = set(), set(), []
        for i, j in pairs:
            if i not in used1 and j not in used2:
                used1.add(i)
                used2.add(j)
                chosen.append((i, j))
    return [(i, j, float(cos[i, j]), float(margin[i, j])) for i, j in chosen]


def best_counterparts(e1: np.ndarray, e2: np.ndarray, k: int) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """For every row of e1: index, cosine and margin of its best counterpart in e2 (and vice versa)."""
    cos, margin, cand = margin_matrix(e1, e2, k)
    scored = np.where(cand, margin, -np.inf)
    f = scored.argmax(axis=1)
    b = scored.argmax(axis=0)
    return f, margin[np.arange(len(e1)), f], b, margin[b, np.arange(len(e2))]


def align_documents(texts1: list[str], texts2: list[str], emb1: np.ndarray, emb2: np.ndarray,
                    alignable1: list[bool], alignable2: list[bool], params: AlignParams,
                    same_language: bool = False) -> dict:
    """Align two segment lists. Returns pairs and, for every unmatched segment, why it is unmatched.

    ``emb1``/``emb2`` hold one row per segment in ``texts1``/``texts2``; rows of non-alignable
    segments are ignored.
    """
    pairs: list[dict] = []
    taken1: set[int] = set()
    taken2: set[int] = set()

    if params.exact_first:
        positions: dict[str, list[int]] = {}
        for j, t in enumerate(texts2):
            if alignable2[j]:
                positions.setdefault(normalize(t), []).append(j)
        for i, t in enumerate(texts1):
            if not alignable1[i]:
                continue
            queue = positions.get(normalize(t))
            if queue:
                j = queue.pop(0)
                taken1.add(i)
                taken2.add(j)
                pairs.append({"src": i, "tgt": j, "cos": 1.0, "margin": None, "kind": "identical"})

    idx1 = [i for i, ok in enumerate(alignable1) if ok and i not in taken1]
    idx2 = [j for j, ok in enumerate(alignable2) if ok and j not in taken2]
    sub1, sub2 = emb1[idx1], emb2[idx2]
    for a, b, c, m in align_embeddings(sub1, sub2, params):
        i, j = idx1[a], idx2[b]
        pairs.append({"src": i, "tgt": j, "cos": round(c, 4), "margin": round(m, 4), "kind": "match"})
        taken1.add(i)
        taken2.add(j)

    if same_language:
        for p in pairs:
            p["char_ratio"] = round(difflib.SequenceMatcher(None, texts1[p["src"]], texts2[p["tgt"]]).ratio(), 3)
    pairs.sort(key=lambda p: (p["src"], p["tgt"]))

    unmatched1, unmatched2 = [], []
    if len(sub1) and len(sub2):
        f, fm, b, bm = best_counterparts(sub1, sub2, params.k)
        matched1 = {p["src"] for p in pairs}
        matched2 = {p["tgt"] for p in pairs}
        for a, i in enumerate(idx1):
            if i not in matched1:
                best = idx2[int(f[a])]
                reason = "weak" if fm[a] < params.min_margin else "taken"
                unmatched1.append({"id": i, "best": best, "margin": round(float(fm[a]), 4), "reason": reason})
        for c, j in enumerate(idx2):
            if j not in matched2:
                best = idx1[int(b[c])]
                reason = "weak" if bm[c] < params.min_margin else "taken"
                unmatched2.append({"id": j, "best": best, "margin": round(float(bm[c]), 4), "reason": reason})
    else:
        matched1 = {p["src"] for p in pairs}
        matched2 = {p["tgt"] for p in pairs}
        unmatched1 = [{"id": i, "best": None, "margin": None, "reason": "weak"} for i in idx1 if i not in matched1]
        unmatched2 = [{"id": j, "best": None, "margin": None, "reason": "weak"} for j in idx2 if j not in matched2]
    return {"pairs": pairs, "unmatched_src": unmatched1, "unmatched_tgt": unmatched2}
