"""Split/merge recovery and preservation of alternative occurrences."""
import numpy as np
import pytest

from wikialigner.align import AlignParams, align_documents
from wikialigner.span_mining import SpanMiningConfig, span_candidates


def norm(x):
    x=np.asarray(x,dtype=np.float32)
    return x/np.maximum(np.linalg.norm(x,axis=1,keepdims=True),1e-12)


def test_reordered_split_group_and_reused_source():
    a=norm([[1,1,0],[0,0,1]])
    b=norm([[0,0,1],[1,0,0],[0,1,0],[0,0,1]])
    gs=span_candidates(a,b,min_margin=.9,config=SpanMiningConfig(top_k=2))
    links={(i,j) for g in gs for i in g['src_ids'] for j in g['tgt_ids']}
    assert (0,1) in links and (0,2) in links
    assert (1,0) in links and (1,3) in links
    # Alternative target occurrences are not consumed by a one-to-one path.
    assert any(g['src_ids']==[0] and g['tgt_ids']==[1,2] for g in gs)


def test_conflicting_segmentation_suppressed_but_exact_group_reused():
    rng=np.random.default_rng(84)
    gs=span_candidates(norm(rng.normal(size=(8,12))),norm(rng.normal(size=(10,12))),min_margin=.5)
    for side in ('src_ids','tgt_ids'):
        for g in gs:
            for h in gs:
                assert not set(g[side]) & set(h[side]) or g[side]==h[side]


def test_group_ids_survive_pipeline_and_size_limit():
    a=norm([[1,0],[0,1]])
    b=norm([[0,1],[1,0],[1,0]])
    r=align_documents(['A','B'],['B','A','A'],a,b,[True]*2,[True]*3,
                      AlignParams(strategy='span',min_margin=.9,exact_first=True))
    assert r['score_unit']=='group'
    assert len([p for p in r['pairs'] if p['src']==0])==2
    assert all('group_id' in p for p in r['pairs'])
    assert span_candidates(np.zeros((0,2)),b)==[]
    with pytest.raises(ValueError,match='too long'):
        span_candidates(a,b,config=SpanMiningConfig(max_cells=2))


def test_span_rejection_does_not_imply_counterpart_is_taken():
    vectors = np.eye(2, dtype=np.float32)
    result = align_documents(["A", "B"], ["C", "D"], vectors, vectors,
                             [True, True], [True, True], AlignParams(strategy="span", min_margin=10))
    assert result["groups"] == []
    assert {entry["reason"] for entry in result["unmatched_src"]} == {"span"}
