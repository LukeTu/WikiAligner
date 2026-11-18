"""Order-preserving alignment with contiguous 1:n, n:1 and n:m groups.

Original implementation: exact dynamic programming on anti-diagonals (NumPy).
No external aligner code is imported. Unlike the order-free matcher, the unit scored
here is a whole contiguous group; expanded links carry the GROUP's score.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np


@dataclass(frozen=True)
class OrderedConfig:
    max_span: int = 4
    max_total: int = 5
    gap_cost: float = 0.02
    merge_cost: float = 0.04
    min_cosine: float = 0.35
    max_cells: int = 1_000_000


def span_vectors(embeddings: np.ndarray, texts: list[str] | None = None,
                 encode: Callable | None = None, max_span: int = 4,
                 indices: list[int] | None = None) -> dict[int, np.ndarray]:
    """Start-indexed normalized vectors of every valid consecutive span.

    The desktop pipeline supplies encode, so multi-sentence strings are encoded
    directly. The normalized mean fallback serves embedding-only callers/ablations.
    Nonconsecutive original indices (e.g. an excluded heading) block a merge.
    """
    n = len(embeddings)
    out = {1: np.asarray(embeddings, dtype=np.float32)}
    pending, locations = [], []
    for size in range(2, min(max_span, n) + 1):
        mat = np.zeros((n - size + 1, embeddings.shape[1]), dtype=np.float32)
        for i in range(len(mat)):
            if indices is not None and indices[i + size - 1] - indices[i] != size - 1:
                continue
            if encode is not None and texts is not None:
                pending.append(' '.join(texts[i:i + size]))
                locations.append((size, i))
            else:
                v = embeddings[i:i + size].mean(axis=0)
                mat[i] = v / max(float(np.linalg.norm(v)), 1e-12)
        out[size] = mat
    if pending:
        for (size, i), v in zip(locations, encode(pending)):
            out[size][i] = v / max(float(np.linalg.norm(v)), 1e-12)
    return out


def _background(e1: np.ndarray, e2: np.ndarray, k: int) -> tuple[np.ndarray, np.ndarray]:
    cos = e1 @ e2.T
    k1, k2 = min(max(k, 1), len(e2)), min(max(k, 1), len(e1))
    return (np.partition(cos, cos.shape[1] - k1, axis=1)[:, -k1:].mean(axis=1),
            np.partition(cos, cos.shape[0] - k2, axis=0)[-k2:, :].mean(axis=0))


def _window_mean(values: np.ndarray, size: int) -> np.ndarray:
    c = np.concatenate(([0.], np.cumsum(values, dtype=np.float64)))
    return ((c[size:] - c[:-size]) / size).astype(np.float32)


def ordered_groups(e1: np.ndarray, e2: np.ndarray, *, k: int = 4,
                   min_margin: float = 1.0, spans1: dict | None = None,
                   spans2: dict | None = None, config: OrderedConfig | None = None) -> list[dict]:
    """Global best monotonic path, followed by the confidence threshold.

    Each transition either skips a sentence or matches two contiguous spans.
    Reward = min(source span, target span) * (ratio margin - 1) - merge penalty.
    Gaps are allowed anywhere, including either document edge. Low-cosine and
    invalid spans cannot match. Thresholding does not re-optimize the path.
    """
    cfg = config or OrderedConfig()
    n, m = len(e1), len(e2)
    if not n or not m:
        return []
    if n * m > cfg.max_cells:
        raise ValueError('Ordered alignment: texts are too long; split them into chapters or sections (max 1 million cells).')
    if not 1 <= cfg.max_span <= 8 or cfg.max_total < 2:
        raise ValueError('Invalid ordered span limits')
    s1 = spans1 if spans1 is not None else span_vectors(e1, max_span=cfg.max_span)
    s2 = spans2 if spans2 is not None else span_vectors(e2, max_span=cfg.max_span)
    b1, b2 = _background(e1, e2, k)
    # Compute a span's background in the SAME opposite singleton space. Averaging
    # singleton backgrounds alone undervalues dissimilar joins and rewards attaching
    # unrelated sentences to a good match.
    bg1 = {a: (b1 if a == 1 else _background(v, e2, k)[0]) for a, v in s1.items()}
    bg2 = {b: (b2 if b == 1 else _background(e1, v, k)[1]) for b, v in s2.items()}
    steps = [(1, 0), (0, 1)] + sorted(
        [(a, b) for a in s1 for b in s2 if a + b <= cfg.max_total],
        key=lambda ab: (sum(ab), abs(ab[0] - ab[1]), ab))
    scores, cosines, margins = {}, {}, {}
    for a, b in steps[2:]:
        cos = (s1[a] @ s2[b].T).astype(np.float32)
        denom = (bg1[a][:, None] + bg2[b][None, :]) / 2
        ratio = np.where(denom > 1e-6, cos / np.maximum(denom, 1e-6), 0).astype(np.float32)
        valid = (cos >= cfg.min_cosine) & (np.linalg.norm(s1[a], axis=1)[:, None] > 0) & (np.linalg.norm(s2[b], axis=1)[None, :] > 0)
        reward = min(a, b) * (ratio - 1) - cfg.merge_cost * (a + b - 2)
        scores[a, b] = np.where(valid, reward, -np.inf)
        cosines[a, b], margins[a, b] = cos, ratio
    dp = np.full((n + 1, m + 1), -np.inf, dtype=np.float64)
    ptr = np.full((n + 1, m + 1), -1, dtype=np.int8)
    dp[0, 0] = 0
    for diagonal in range(1, n + m + 1):
        ii = np.arange(max(0, diagonal - m), min(n, diagonal) + 1)
        jj = diagonal - ii
        best = np.full(len(ii), -np.inf)
        choice = np.full(len(ii), -1, dtype=np.int8)
        for step, (a, b) in enumerate(steps):
            valid = (ii >= a) & (jj >= b)
            x, y = ii[valid], jj[valid]
            gain = -cfg.gap_cost if a == 0 or b == 0 else scores[a, b][x - a, y - b]
            val = dp[x - a, y - b] + gain
            hit = np.flatnonzero(valid)
            better = val > best[hit]
            best[hit[better]] = val[better]
            choice[hit[better]] = step
        dp[ii, jj], ptr[ii, jj] = best, choice
    groups = []
    i, j = n, m
    while i or j:
        step = int(ptr[i, j])
        if step < 0:
            raise RuntimeError('Ordered path is incomplete')
        a, b = steps[step]
        if a and b:
            confidence = float(margins[a, b][i - a, j - b])
            if confidence >= min_margin:
                groups.append({'src_ids': list(range(i - a, i)), 'tgt_ids': list(range(j - b, j)),
                               'cos': round(float(cosines[a, b][i - a, j - b]), 4),
                               'margin': round(confidence, 4), 'kind': 'match'})
        i, j = i - a, j - b
    return list(reversed(groups))
