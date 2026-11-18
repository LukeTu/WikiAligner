"""Regression: whole-span reward must not swallow separate gold groups."""
from dataclasses import replace

import numpy as np

from wikialigner.ordered import OrderedConfig as OldConfig,ordered_groups as old_groups
from wikialigner.ordered_refined import OrderedConfig,ordered_groups,prepare_alignment,decode_alignment
from wikialigner.align import AlignParams,align_documents


def test_separate_pairs_survive_semantically_coherent_concatenations():
    # Four correct singletons share a topic. Concatenation has additional common
    # context: its embedding differs from an average of singleton embeddings.
    e=np.zeros((4,6),dtype=np.float32);e[:,0]=.8
    for i in range(4):e[i,i+1]=.6
    span=np.zeros(6,dtype=np.float32);span[0]=.78125;span[5]=np.sqrt(1-span[0]**2)
    spans={1:e,2:np.tile(span,(3,1))}
    old=old_groups(e,e,spans1=spans,spans2=spans,min_margin=.9,config=OldConfig(merge_cost=.08))
    assert any(len(g['src_ids'])>1 and len(g['tgt_ids'])>1 for g in old)
    new=ordered_groups(e,e,spans1=spans,spans2=spans,min_margin=.9)
    assert [(g['src_ids'],g['tgt_ids']) for g in new]==[([i],[i]) for i in range(4)]


def test_soft_corridor_and_threshold_keep_a_valid_monotone_path():
    e=np.eye(6,dtype=np.float32)
    prep=prepare_alignment(e,e)
    cfg=OrderedConfig(band_width=1,threshold_inside=True)
    groups=decode_alignment(prep,config=cfg,min_margin=.9)
    assert [(g['src_ids'],g['tgt_ids']) for g in groups]==[([i],[i]) for i in range(6)]
    assert decode_alignment(prep,config=cfg,min_margin=10.)==[]
    assert ordered_groups(np.zeros((0,6)),e)==[]


def test_rejected_path_groups_remain_available_for_review():
    e=np.eye(2,dtype=np.float32)
    r=align_documents(['A','B'],['a','b'],e,e,[True]*2,[True]*2,
                      AlignParams(strategy='ordered',min_margin=10.))
    assert r['pairs']==[] and r['groups']==[]
    assert [(g['src_ids'],g['tgt_ids']) for g in r['low_confidence_groups']]==[([0],[0]),([1],[1])]
    assert all(g['status']=='below_threshold' and g['above_threshold'] is False for g in r['low_confidence_groups'])
