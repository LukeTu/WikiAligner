import numpy as np
import pytest

from wikialigner.align import AlignParams, align_documents, align_embeddings, margin_matrix


def unit(rows):
    a = np.asarray(rows, dtype=np.float32)
    return a / np.linalg.norm(a, axis=1, keepdims=True)


def test_short_documents_still_align():
    # The first version used k=4 regardless of length, so a two-sentence article got no pairs.
    e1 = unit([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
    e2 = unit([[0.05, 1, 0], [1, 0.05, 0]])
    pairs = align_embeddings(e1, e2, AlignParams(k=4))
    assert {(i, j) for i, j, *_ in pairs} == {(0, 1), (1, 0)}


def test_any_embedding_dimension(fake_embedder):
    e = fake_embedder.encode(["c1 a", "c2 b"])
    assert e.shape[1] == 32
    pairs = align_embeddings(e, fake_embedder.encode(["c2 x", "c1 y"]), AlignParams())
    assert {(i, j) for i, j, *_ in pairs} == {(0, 1), (1, 0)}


def test_margin_is_finite_and_candidates_limited():
    rng = np.random.default_rng(0)
    e1, e2 = unit(rng.normal(size=(6, 8))), unit(rng.normal(size=(3, 8)))
    cos, margin, cand = margin_matrix(e1, e2, k=4)
    assert np.isfinite(margin).all()
    assert cand.any(axis=1).all() and cand.any(axis=0).all()


def test_greedy_is_one_to_one_and_many_allows_splits(fake_embedder):
    left = ["c1 one long sentence", "c2 another sentence"]
    right = ["c1 first half", "c1 second half", "c2 the other"]
    e1, e2 = fake_embedder.encode(left), fake_embedder.encode(right)
    greedy = align_embeddings(e1, e2, AlignParams(strategy="greedy", min_margin=0.9))
    assert len({i for i, *_ in greedy}) == len(greedy) and len({j for _, j, *_ in greedy}) == len(greedy)
    many = align_embeddings(e1, e2, AlignParams(strategy="many", min_margin=0.9))
    assert {(0, 0), (0, 1)} <= {(i, j) for i, j, *_ in many}


def test_unmatched_segments_get_a_reason(fake_embedder):
    left = ["c1 one", "c2 two", "c3 three"]
    right = ["c1 uno", "c2 dos", "c9 unrelated"]
    r = align_documents(left, right, fake_embedder.encode(left), fake_embedder.encode(right),
                        [True] * 3, [True] * 3, AlignParams(min_margin=1.02))
    matched = {(p["src"], p["tgt"]) for p in r["pairs"]}
    assert (0, 0) in matched and (1, 1) in matched
    assert all(u["reason"] in ("weak", "taken") for u in r["unmatched_src"] + r["unmatched_tgt"])


def test_revision_mode_pairs_identical_sentences_first(fake_embedder):
    old = ["c1 Same sentence.", "c2 Old wording here.", "c3 Removed later."]
    new = ["c1 Same sentence.", "c2 New wording here.", "c4 Added later."]
    r = align_documents(old, new, fake_embedder.encode(old), fake_embedder.encode(new), [True] * 3, [True] * 3,
                        AlignParams(exact_first=True, min_margin=1.0), same_language=True)
    kinds = {(p["src"], p["tgt"]): p for p in r["pairs"]}
    assert kinds[(0, 0)]["kind"] == "identical" and kinds[(0, 0)]["char_ratio"] == 1.0
    assert kinds[(1, 1)]["kind"] == "match" and 0.5 < kinds[(1, 1)]["char_ratio"] < 1.0


def test_non_alignable_segments_are_skipped(fake_embedder):
    left, right = ["Heading", "c1 text"], ["c1 texto"]
    r = align_documents(left, right, fake_embedder.encode(left), fake_embedder.encode(right),
                        [False, True], [True], AlignParams())
    assert [(p["src"], p["tgt"]) for p in r["pairs"]] == [(1, 0)]
    assert r["unmatched_src"] == []


def test_unknown_strategy_raises():
    with pytest.raises(ValueError):
        align_embeddings(unit([[1, 0]]), unit([[1, 0]]), AlignParams(strategy="nope"))
