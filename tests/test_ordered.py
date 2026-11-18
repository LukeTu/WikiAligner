"""Properties of the new ordered path, including split/merge and skip transitions."""
import numpy as np
import pytest

from wikialigner.align import AlignParams, align_documents, align_embeddings
from wikialigner.ordered import span_vectors
from wikialigner.ordered_refined import OrderedConfig, ordered_groups
from wikialigner.pipeline import AlignOptions, SourceSpec, run_alignment


def unit(x):
    x = np.asarray(x, dtype=np.float32)
    return x / np.maximum(np.linalg.norm(x, axis=1, keepdims=True), 1e-12)


def test_split_merge_and_gaps():
    # An inserted unrelated target and two target sentences for the first source.
    a = unit([[1, 1, 0, 0], [0, 0, 1, 0]])
    b = unit([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]])
    gs = ordered_groups(a, b, min_margin=0.)
    assert [(g['src_ids'], g['tgt_ids']) for g in gs] == [([0], [0, 1]), ([1], [3])]
    reverse = ordered_groups(b, a, min_margin=0.)
    assert [(g['src_ids'], g['tgt_ids']) for g in reverse] == [([0, 1], [0]), ([3], [1])]


def test_monotonic_path_does_not_reuse_or_cross():
    rng = np.random.default_rng(19)
    a, b = unit(rng.normal(size=(13, 16))), unit(rng.normal(size=(10, 16)))
    gs = ordered_groups(a, b, min_margin=0.)
    for prev, nxt in zip(gs, gs[1:]):
        assert max(prev['src_ids']) < min(nxt['src_ids'])
        assert max(prev['tgt_ids']) < min(nxt['tgt_ids'])


def test_many_to_many_group_uses_complete_semantic_unit():
    # Each side partitions the same four semantic components differently.
    a=unit([[1,0,1,0],[0,1,0,1]])
    b=unit([[1,1,0,0],[0,0,1,1]])
    gs=ordered_groups(a,b,min_margin=1.)
    assert [(g['src_ids'],g['tgt_ids']) for g in gs]==[([0,1],[0,1])]


def test_exact_first_does_not_introduce_crossing_in_ordered_mode(fake_embedder):
    left, right = ['c1 A', 'c2 B', 'c3 C'], ['c2 B', 'c1 A', 'c3 C']
    r = align_documents(left, right, fake_embedder.encode(left), fake_embedder.encode(right),
                        [True]*3, [True]*3, AlignParams(strategy='ordered', exact_first=True),
                        same_language=True)
    gs = r['groups']
    assert sum(g['kind'] == 'identical' for g in gs) == 2
    for g, h in zip(gs, gs[1:]):
        assert max(g['src_ids']) < min(h['src_ids']) and max(g['tgt_ids']) < min(h['tgt_ids'])
    assert r['score_unit'] == 'group'


def test_spans_do_not_merge_across_excluded_heading():
    a = np.eye(3, dtype=np.float32)
    spans = span_vectors(a, indices=[0, 2, 3])
    assert not spans[2][0].any() and spans[2][1].any()
    assert not spans[3].any()


def test_pipeline_keeps_ids_and_group_scores():
    a, b = unit([[1, 1, 0], [0, 0, 1]]), np.eye(3, dtype=np.float32)
    a = np.vstack((a[0], [0, 0, 0], a[1]))
    r = align_documents(['long', 'heading', 'end'], ['first', 'second', 'last'], a, b,
                        [True, False, True], [True]*3, AlignParams(strategy='ordered', min_margin=0.))
    assert [(g['src_ids'], g['tgt_ids']) for g in r['groups']] == [([0], [0, 1]), ([2], [2])]
    assert {(p['src'], p['tgt']) for p in r['pairs']} == {(0, 0), (0, 1), (2, 2)}
    assert len({p['margin'] for p in r['pairs'] if p['group_id']==0}) == 1


def test_empty_unrelated_threshold_and_size_guard():
    assert ordered_groups(np.zeros((0, 3)), np.eye(3)) == []
    assert ordered_groups(unit([[1, 0]]), unit([[0, 1]])) == []
    assert ordered_groups(np.eye(2), np.eye(2), min_margin=10.) == []
    with pytest.raises(ValueError, match='too long'):
        ordered_groups(np.eye(2), np.eye(2), config=OrderedConfig(max_cells=3))
    assert AlignOptions.from_dict({'strategy':'ordered'}).strategy == 'ordered'
    with pytest.raises(ValueError):
        AlignOptions.from_dict({'strategy':'unrecognised'})


def test_embedding_only_entrypoint_is_consistent():
    a, b = unit([[1, 1, 0], [0, 0, 1]]), np.eye(3, dtype=np.float32)
    links = {(i, j) for i,j,*_ in align_embeddings(a,b,AlignParams(strategy='ordered',min_margin=0.))}
    groups = ordered_groups(a,b,min_margin=0.)
    assert links == {(i,j) for g in groups for i in g['src_ids'] for j in g['tgt_ids']}


@pytest.mark.parametrize("strategy", ["ordered", "span"])
def test_size_limit_checked_before_loading_model(strategy):
    class UnusedModelManager:
        def get(self, *args):
            pytest.fail("model was loaded for a job above the group size limit")

    text = "\n\n".join(f"Sentence {i}." for i in range(1001))
    source = SourceSpec(type="text", text=text)
    with pytest.raises(ValueError, match="too long"):
        run_alignment(source, source, AlignOptions(strategy=strategy), None, UnusedModelManager())
