"""Margin-based sentence matching between two documents.

Scores follow Artetxe & Schwenk (2019): the ratio margin divides the cosine of a pair by
the average cosine of each side's k nearest neighbours, which corrects for "hub" sentences
that are close to everything. The candidate search and greedy one-to-one selection follow
the sentence-transformers bitext-mining example (Apache-2.0), rewritten in vectorised NumPy
so that k never exceeds the number of available sentences.
"""
from __future__ import annotations

import difflib
from collections import defaultdict, deque
from dataclasses import asdict, dataclass

import numpy as np

from .ordered import span_vectors
from .ordered_refined import OrderedConfig, ordered_groups
from .span_mining import SpanMiningConfig, span_candidates

GROUP_STRATEGIES = ("ordered", "span")
STRATEGIES = ("greedy", "mutual", "many", *GROUP_STRATEGIES)
GROUP_CONFIGS = {"ordered": OrderedConfig(), "span": SpanMiningConfig()}


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


def check_alignment_size(strategy: str, n1: int, n2: int) -> None:
    config = GROUP_CONFIGS.get(strategy)
    if config is not None and n1 * n2 > config.max_cells:
        label = "In-order alignment" if strategy == "ordered" else "Span candidate search"
        raise ValueError(f"{label}: texts are too long. Split them into chapters or sections "
                         f"(maximum {config.max_cells:,} segment combinations).")


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
    if params.strategy in GROUP_STRATEGIES:
        matcher = ordered_groups if params.strategy == "ordered" else span_candidates
        return [(i, j, g["cos"], g["margin"]) for g in matcher(e1, e2, k=params.k, min_margin=params.min_margin)
                for i in g["src_ids"] for j in g["tgt_ids"]]
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


def _unmatched_segments(indices, other_indices, matched, closest, margins, params):
    unmatched = []
    for pos, segment_id in enumerate(indices):
        if segment_id in matched:
            continue
        if closest is None:
            unmatched.append({"id": segment_id, "best": None, "margin": None, "reason": "no_candidate"})
            continue
        margin = float(margins[pos])
        if params.strategy == "ordered":
            reason = "order"
        elif params.strategy == "span":
            reason = "span"
        else:
            reason = "weak" if margin < params.min_margin else "taken"
        unmatched.append({"id": segment_id, "best": other_indices[int(closest[pos])],
                          "margin": round(margin, 4), "reason": reason})
    return unmatched


def align_documents(texts1: list[str], texts2: list[str], emb1: np.ndarray, emb2: np.ndarray,
                    alignable1: list[bool], alignable2: list[bool], params: AlignParams,
                    same_language: bool = False, span_encoder=None) -> dict:
    """Align two segment lists. Returns pairs and, for every unmatched segment, why it is unmatched.

    ``emb1``/``emb2`` hold one row per segment in ``texts1``/``texts2``; rows of non-alignable
    segments are ignored.
    """
    pairs: list[dict] = []
    groups, low_confidence_groups = [], []
    idx1 = [i for i, ok in enumerate(alignable1) if ok]
    idx2 = [j for j, ok in enumerate(alignable2) if ok]
    check_alignment_size(params.strategy, len(idx1), len(idx2))
    group_mode = params.strategy in GROUP_STRATEGIES
    exact_first = params.exact_first and (same_language or not group_mode)

    def add_group(group):
        group_id = len(groups)
        groups.append({**group, "id": group_id})
        for i in group["src_ids"]:
            for j in group["tgt_ids"]:
                pairs.append({"src": i, "tgt": j, "cos": group["cos"], "margin": group["margin"],
                              "kind": group["kind"], "group_id": group_id})

    if exact_first and params.strategy != "ordered":
        positions = defaultdict(deque)
        for j in idx2:
            positions[normalize(texts2[j])].append(j)
        for i in idx1:
            queue = positions.get(normalize(texts1[i]))
            if not queue:
                continue
            j = queue.popleft()
            equal_score = {"cos": 1.0, "margin": None, "kind": "identical"}
            if group_mode:
                add_group({**equal_score, "src_ids": [i], "tgt_ids": [j]})
            else:
                pairs.append({"src": i, "tgt": j, **equal_score})
        exact_src = {p["src"] for p in pairs}
        exact_tgt = {p["tgt"] for p in pairs}
        idx1 = [i for i in idx1 if i not in exact_src]
        idx2 = [j for j in idx2 if j not in exact_tgt]

    sub1, sub2 = emb1[idx1], emb2[idx2]
    if group_mode and len(sub1) and len(sub2):
        left = [texts1[i] for i in idx1]
        right = [texts2[j] for j in idx2]
        config = GROUP_CONFIGS[params.strategy]
        spans1 = span_vectors(sub1, left, span_encoder, max_span=config.max_span, indices=idx1)
        spans2 = span_vectors(sub2, right, span_encoder, max_span=config.max_span, indices=idx2)
        if params.strategy == "ordered":
            exact_matches = None
            if exact_first:
                literal1 = np.asarray([normalize(text) for text in left], dtype=object)
                literal2 = np.asarray([normalize(text) for text in right], dtype=object)
                exact_matches = literal1[:, None] == literal2[None, :]
            candidates = ordered_groups(sub1, sub2, k=params.k, min_margin=0.,
                                        spans1=spans1, spans2=spans2, config=config,
                                        review_threshold=params.min_margin, exact_matches=exact_matches)
        else:
            candidates = span_candidates(sub1, sub2, k=params.k, min_margin=params.min_margin,
                                         spans1=spans1, spans2=spans2, config=config)
        for g in candidates:
            g = {**g, "src_ids": [idx1[i] for i in g["src_ids"]],
                 "tgt_ids": [idx2[j] for j in g["tgt_ids"]]}
            if g.get("above_threshold") is False:
                low_confidence_groups.append({**g, "id": f"low-{len(low_confidence_groups)}",
                                              "status": "below_threshold"})
                continue
            if same_language and len(g["src_ids"]) == len(g["tgt_ids"]) == 1:
                if normalize(texts1[g["src_ids"][0]]) == normalize(texts2[g["tgt_ids"][0]]):
                    g.update(kind="identical", cos=1., margin=None)
            add_group(g)
    elif not group_mode:
        for a, b, c, m in align_embeddings(sub1, sub2, params):
            i, j = idx1[a], idx2[b]
            pairs.append({"src": i, "tgt": j, "cos": round(c, 4), "margin": round(m, 4), "kind": "match"})

    if same_language:
        for p in pairs:
            if "group_id" in p:
                group = groups[p["group_id"]]
                if len(group["src_ids"]) != 1 or len(group["tgt_ids"]) != 1:
                    continue
            p["char_ratio"] = round(difflib.SequenceMatcher(None, texts1[p["src"]], texts2[p["tgt"]]).ratio(), 3)
    pairs.sort(key=lambda p: (p["src"], p["tgt"]))

    matched1 = {p["src"] for p in pairs}
    matched2 = {p["tgt"] for p in pairs}
    if len(sub1) and len(sub2):
        f, fm, b, bm = best_counterparts(sub1, sub2, params.k)
    else:
        f = fm = b = bm = None
    unmatched1 = _unmatched_segments(idx1, idx2, matched1, f, fm, params)
    unmatched2 = _unmatched_segments(idx2, idx1, matched2, b, bm, params)
    algorithm = {"name": params.strategy}
    if params.strategy == "ordered":
        algorithm.update(version="ordered-refined-v2", settings=asdict(GROUP_CONFIGS["ordered"]))
    elif params.strategy == "span":
        algorithm.update(version="span-candidates-v1", settings=asdict(GROUP_CONFIGS["span"]))
    return {"pairs": pairs, "unmatched_src": unmatched1, "unmatched_tgt": unmatched2,
            "groups": groups, "score_unit": "group" if group_mode else "sentence",
            "alignment_algorithm": algorithm, "low_confidence_groups": low_confidence_groups}
