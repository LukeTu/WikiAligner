"""Group-boundary oriented monotonic alignment.

Independent NumPy implementation. Local contrast and length consistency are
motivated by Liu & Zhu's Bertalign (doi:10.1093/llc/fqac089). No external aligner
implementation is imported. The initial ratio decoder remains in ordered.py for
the frozen exploratory comparison.
"""
from __future__ import annotations

from bisect import bisect_left
from dataclasses import dataclass, replace

import numpy as np

from .ordered import _background, span_vectors


@dataclass(frozen=True)
class OrderedConfig:
    max_span: int = 4
    max_total: int = 5
    gap_cost: float = .10
    merge_cost: float = .04
    min_cosine: float = .35
    max_cells: int = 1_000_000
    scoring: str = 'local_contrast'
    threshold_inside: bool = False
    band_width: int = 0


def _outside(v, width):
    n,d=v.shape;out=np.zeros((n-width+1,d),np.float32);count=np.zeros(len(out))
    for i in range(len(out)):
        if i:out[i]+=v[i-1];count[i]+=1
        if i+width<n:out[i]+=v[i+width];count[i]+=1
    return out/np.maximum(count[:,None],1.)


def _lengths(single, width):
    c=np.r_[0.,np.cumsum(single,dtype=np.float64)]
    return c[width:]-c[:-width]+width-1


def prepare_alignment(e1,e2,*,spans1=None,spans2=None,lengths1=None,lengths2=None,
                      k=4,config=None):
    cfg=config or OrderedConfig();n,m=len(e1),len(e2)
    if not 1<=cfg.max_span<=8 or cfg.max_total<2 or cfg.band_width<0:
        raise ValueError('Invalid ordered span or search limits')
    if n*m>cfg.max_cells:
        raise ValueError('Ordered alignment: texts are too long; split them into chapters or sections (max 1 million cells).')
    if not n or not m:return None
    if cfg.scoring not in {'ratio','local_contrast','local_length'}:
        raise ValueError('Unknown ordered scoring method')
    a=spans1 if spans1 is not None else span_vectors(e1,max_span=cfg.max_span)
    b=spans2 if spans2 is not None else span_vectors(e2,max_span=cfg.max_span)
    bg1={s:_background(v,e2,k)[0] for s,v in a.items()}
    bg2={s:_background(e1,v,k)[1] for s,v in b.items()}
    near1={s:_outside(e1,s) for s in a};near2={s:_outside(e2,s) for s in b}
    lens_available=lengths1 is not None and lengths2 is not None
    if lens_available:
        l1={s:_lengths(lengths1,s) for s in a};l2={s:_lengths(lengths2,s) for s in b}
        ratio=(sum(lengths1)+n-1)/(sum(lengths2)+m-1)
    surfaces={}
    for u,x in a.items():
        for v,y in b.items():
            if u+v>cfg.max_total:continue
            cos=np.clip(x@y.T,-1.,1.).astype(np.float32)
            den=(bg1[u][:,None]+bg2[v][None,:])/2
            margin=np.where(den>1e-6,cos/np.maximum(den,1e-6),0.)
            contrast=(x@near2[v].T+near1[u]@y.T)/2
            local=cos-contrast
            factor=1.
            if lens_available:
                aa=l1[u][:,None];bb=l2[v][None,:]*ratio
                factor=np.minimum(aa,bb)/np.maximum(np.maximum(aa,bb),1e-9)
            surfaces[u,v]={'cos':cos,'margin':margin.astype(np.float32),
                'ratio':(margin-1.).astype(np.float32),
                'local_contrast':local.astype(np.float32),
                'local_length':(local*factor).astype(np.float32),
                'valid':(cos>=cfg.min_cosine)&(np.linalg.norm(x,axis=1)[:,None]>0)&(np.linalg.norm(y,axis=1)[None,:]>0)}
    return {'n':n,'m':m,'surfaces':surfaces,'single_cos':surfaces[1,1]['cos'],
            'single_margin':surfaces[1,1]['margin'],'length_penalty_available':lens_available}


def _corridor(prepared,width):
    cos=prepared['single_cos'];marg=prepared['single_margin'];n,m=cos.shape
    best=cos.argmax(axis=1);back=cos.argmax(axis=0)
    anchors=[(i,int(j)) for i,j in enumerate(best) if back[j]==i and cos[i,j]>=.55 and marg[i,j]>=1.05]
    # A longest increasing chain; anchors constrain a corridor, never force pairs.
    tails=[];indices=[];previous=[]
    for t,(_,j) in enumerate(anchors):
        pos=bisect_left(tails,j);previous.append(indices[pos-1] if pos else -1)
        if pos==len(tails):tails.append(j);indices.append(t)
        else:tails[pos]=j;indices[pos]=t
    chain=[];cur=indices[-1] if indices else -1
    while cur>=0:chain.append(anchors[cur]);cur=previous[cur]
    chain=list(reversed(chain))
    points=[(0,0)]+[(i+1,j+1) for i,j in chain if i+1<n and j+1<m]+[(n,m)]
    center=np.interp(np.arange(n+1),[p[0] for p in points],[p[1] for p in points])
    return center,width,len(chain)


def decode_alignment(prepared, *, config=None, min_margin=1., review_threshold=None,
                     exact_matches: np.ndarray | None = None):
    """Choose a monotone path, prioritizing identical 1:1 links when requested."""
    if prepared is None:
        return []
    cfg = config or OrderedConfig()
    n, m = prepared["n"], prepared["m"]
    surfaces = prepared["surfaces"]
    steps = [(1, 0), (0, 1)] + sorted(surfaces, key=lambda s: (sum(s), abs(s[0] - s[1]), s))
    if exact_matches is not None:
        if exact_matches.shape != (n, m):
            raise ValueError("Exact match mask must match the two document lengths")
        if not exact_matches.any():
            exact_matches = None

    gains = {}
    for (a, b), surface in surfaces.items():
        valid = surface["valid"]
        if cfg.threshold_inside:
            valid = valid & (surface["margin"] >= min_margin)
        gain = surface[cfg.scoring] - cfg.merge_cost * (a + b - 2)
        if exact_matches is not None and (a, b) == (1, 1):
            valid = valid | exact_matches
            gain = np.where(exact_matches, 0., gain)
        gains[a, b] = np.where(valid, gain, -np.inf)
    band = _corridor(prepared, cfg.band_width) if cfg.band_width else None
    dp = np.full((n + 1, m + 1), -np.inf, dtype=np.float64)
    ptr = np.full((n + 1, m + 1), -1, dtype=np.int8)
    dp[0, 0] = 0.
    # Keep exact counts separate from scores so the comparison is independent of
    # similarity scale and the cross-language path uses its regular objective.
    exact_counts = np.zeros((n + 1, m + 1), dtype=np.int32) if exact_matches is not None else None
    for diagonal in range(1, n + m + 1):
        ii = np.arange(max(0, diagonal - m), min(n, diagonal) + 1)
        jj = diagonal - ii
        if band:
            keep = np.abs(jj - band[0][ii]) <= band[1]
            ii, jj = ii[keep], jj[keep]
        if not len(ii):
            continue
        best = np.full(len(ii), -np.inf)
        choices = np.full(len(ii), -1, dtype=np.int8)
        best_exact = np.full(len(ii), -1, dtype=np.int32) if exact_counts is not None else None
        for step, (a, b) in enumerate(steps):
            mask = (ii >= a) & (jj >= b)
            x, y = ii[mask] - a, jj[mask] - b
            gain = gains[a, b][x, y] if a and b else -cfg.gap_cost
            score = dp[x, y] + gain
            at = np.flatnonzero(mask)
            better = score > best[at]
            if exact_counts is not None:
                count = exact_counts[x, y]
                if (a, b) == (1, 1):
                    count = count + exact_matches[x, y]
                previous_count = best_exact[at]
                better = np.isfinite(score) & ((count > previous_count) | ((count == previous_count) & better))
                best_exact[at[better]] = count[better]
            best[at[better]] = score[better]
            choices[at[better]] = step
        dp[ii, jj], ptr[ii, jj] = best, choices
        if exact_counts is not None:
            exact_counts[ii, jj] = best_exact

    if not np.isfinite(dp[n, m]):
        if band:
            groups = decode_alignment(prepared, config=replace(cfg, band_width=0), min_margin=min_margin,
                                      review_threshold=review_threshold, exact_matches=exact_matches)
            for group in groups:
                group["band_fallback"] = True
            return groups
        raise RuntimeError("Ordered path is incomplete")

    groups = []
    i, j = n, m
    while i or j:
        step = int(ptr[i, j])
        if step < 0:
            raise RuntimeError("Ordered backtrack is incomplete")
        a, b = steps[step]
        if a and b:
            x, y = i - a, j - b
            surface = surfaces[a, b]
            confidence = float(surface["margin"][x, y])
            identical = exact_matches is not None and (a, b) == (1, 1) and exact_matches[x, y]
            if identical or confidence >= min_margin:
                group = {"src_ids": list(range(x, i)), "tgt_ids": list(range(y, j)),
                         "cos": 1.0 if identical else round(float(surface["cos"][x, y]), 4),
                         "margin": None if identical else round(confidence, 4),
                         "alignment_score": None if identical else round(float(gains[a, b][x, y]), 4),
                         "kind": "identical" if identical else "match", "algorithm": "ordered-refined-v2"}
                if review_threshold is not None:
                    group["above_threshold"] = bool(identical or confidence >= review_threshold)
                groups.append(group)
        i, j = i - a, j - b
    return list(reversed(groups))


def ordered_groups(e1, e2, *, k=4, min_margin=1., spans1=None, spans2=None, lengths1=None,
                   lengths2=None, config=None, review_threshold=None, exact_matches=None):
    cfg = config or OrderedConfig()
    prepared = prepare_alignment(e1, e2, k=k, spans1=spans1, spans2=spans2,
                                  lengths1=lengths1, lengths2=lengths2, config=cfg)
    return decode_alignment(prepared, config=cfg, min_margin=min_margin,
                            review_threshold=review_threshold, exact_matches=exact_matches)
