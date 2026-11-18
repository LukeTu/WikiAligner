"""Order-free span candidates with reusable, explicit sentence groups.

Unlike a document alignment path, this is a candidate graph. Exact groups can be
reused at multiple locations; incompatible overlapping segmentations are suppressed.
Scores describe groups, never translation provenance or individual expanded links.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .ordered import _background, span_vectors


@dataclass(frozen=True)
class SpanMiningConfig:
    max_span: int = 4
    max_total: int = 5
    top_k: int = 2
    merge_cost: float = .02
    min_cosine: float = .35
    max_cells: int = 1_000_000


def span_candidates(e1: np.ndarray, e2: np.ndarray, *, k: int = 4,
                    min_margin: float = 1., spans1: dict | None = None,
                    spans2: dict | None = None,
                    config: SpanMiningConfig | None = None) -> list[dict]:
    """Reciprocal top-k span retrieval followed by overlap suppression.

    All span lengths compete for each source/target start-and-length identity.
    Ranking subtracts a merge cost from the ratio margin; the reported margin is
    the original group margin. There is no monotonic constraint or exclusive
    consumption of an exact group. This returns hypotheses for inspection.
    """
    cfg = config or SpanMiningConfig()
    n, m = len(e1), len(e2)
    if not n or not m:
        return []
    if n*m > cfg.max_cells:
        raise ValueError('Span mining: texts are too long; split them into chapters or sections (max 1 million cells).')
    if cfg.top_k < 1 or not 1 <= cfg.max_span <= 8 or cfg.max_total < 2:
        raise ValueError('Invalid span candidate settings')
    s1 = spans1 if spans1 is not None else span_vectors(e1, max_span=cfg.max_span)
    s2 = spans2 if spans2 is not None else span_vectors(e2, max_span=cfg.max_span)
    bg1 = {a: _background(v, e2, k)[0] for a,v in s1.items()}
    bg2 = {b: _background(e1, v, k)[1] for b,v in s2.items()}
    # Only per-span top-k edges are retained, keeping the candidate graph compact.
    forward, backward = {}, {}
    for a, x in s1.items():
        for b, y in s2.items():
            if a+b > cfg.max_total:
                continue
            cos = x @ y.T
            denom = (bg1[a][:,None] + bg2[b][None,:])/2
            ratio = np.where(denom>1e-6, cos/np.maximum(denom,1e-6), 0.)
            valid = ((cos>=cfg.min_cosine) & (ratio>=min_margin)
                     & (np.linalg.norm(x,axis=1)[:,None]>0)
                     & (np.linalg.norm(y,axis=1)[None,:]>0))
            score = np.where(valid,ratio-cfg.merge_cost*(a+b-2),-np.inf)
            for i in range(len(x)):
                js=np.argsort(-score[i],kind='stable')[:cfg.top_k]
                dest=forward.setdefault((a,i),[])
                dest.extend((float(score[i,j]),a,i,b,int(j),float(cos[i,j]),float(ratio[i,j]))
                            for j in js if np.isfinite(score[i,j]))
            for j in range(len(y)):
                ii=np.argsort(-score[:,j],kind='stable')[:cfg.top_k]
                dest=backward.setdefault((b,j),[])
                dest.extend((float(score[i,j]),a,int(i),b,j,float(cos[i,j]),float(ratio[i,j]))
                            for i in ii if np.isfinite(score[i,j]))
    def ranked(values):
        return sorted(values,key=lambda x:(-x[0],x[1]+x[3],x[1:5]))[:cfg.top_k]
    f={v[1:5]:v for values in forward.values() for v in ranked(values)}
    r={v[1:5] for values in backward.values() for v in ranked(values)}
    chosen=[]
    left_used, right_used = {}, {}
    for v in sorted((v for key,v in f.items() if key in r),
                    key=lambda x:(-x[0],x[1]+x[3],x[1:5])):
        score,a,i,b,j,cos,margin=v
        left=tuple(range(i,i+a));right=tuple(range(j,j+b))
        if any(p in left_used and left_used[p]!=left for p in left):
            continue
        if any(p in right_used and right_used[p]!=right for p in right):
            continue
        left_used.update((p,left) for p in left)
        right_used.update((p,right) for p in right)
        chosen.append({'src_ids':list(left),'tgt_ids':list(right),
                       'cos':round(cos,4),'margin':round(margin,4),
                       'ranking_score':round(score,4),'kind':'match'})
    return sorted(chosen,key=lambda g:(g['src_ids'],g['tgt_ids']))
