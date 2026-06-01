"""Diversity metrics over a set of artifact embeddings / texts.

Semantic dispersion is the headline. Effective dimensionality and lexical
diversity sit alongside it so we can tell *semantic* collapse from mere
wording overlap.

Anisotropy note: raw text-embedding-3 space is anisotropic (a dominant common
direction inflates all cosine similarities). The standard, non-degenerate fix at
small n is to subtract a global mean embedding ("all-but-the-mean") and recompute
cosine. We deliberately do NOT full-whiten: estimating a 1536x1536 covariance from
~12 points is rank-deficient and maps the points to a regular simplex, destroying
the very structure we measure. Mean-centering needs only a single shared vector.
"""
from __future__ import annotations

import numpy as np


def global_mean(emb_pool: np.ndarray) -> np.ndarray:
    """Mean embedding over a large reference pool (all artifacts in the run)."""
    return emb_pool.mean(axis=0)


def center(emb: np.ndarray, mean: np.ndarray) -> np.ndarray:
    return emb - mean


def _l2norm(emb: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(emb, axis=1, keepdims=True)
    n = np.clip(n, 1e-12, None)
    return emb / n


def semantic_dispersion(emb: np.ndarray) -> float:
    """Mean pairwise cosine distance (1 - cos). Higher = more diverse."""
    u = _l2norm(emb)
    sims = u @ u.T
    n = u.shape[0]
    iu = np.triu_indices(n, k=1)
    d = 1.0 - sims[iu]
    return float(d.mean())


def participation_ratio(emb: np.ndarray) -> float:
    """Effective dimensionality = (sum of eigenvalues)^2 / sum(eigenvalues^2).

    Computed on the per-set covariance. Bounded above by min(n-1, d); a population
    spread evenly across k directions scores ~k, one collapsing onto a line -> ~1.
    Non-degenerate at small n (unlike whitening), and varies with real structure.
    """
    X = emb - emb.mean(axis=0)
    if X.shape[0] < 2:
        return 1.0
    cov = np.cov(X, rowvar=False)
    vals = np.linalg.eigvalsh(cov)
    vals = np.clip(vals, 0, None)
    s1 = vals.sum()
    s2 = (vals ** 2).sum()
    if s2 <= 0:
        return 1.0
    return float((s1 ** 2) / s2)


def _tokens(text: str) -> list[str]:
    return [t for t in text.lower().replace("\n", " ").split(" ") if t]


def distinct_2(texts: list[str]) -> float:
    """Fraction of distinct bigrams across the corpus. Higher = more lexical variety."""
    total, seen = 0, set()
    for t in texts:
        toks = _tokens(t)
        for i in range(len(toks) - 1):
            seen.add((toks[i], toks[i + 1]))
            total += 1
    return float(len(seen) / total) if total else 0.0


def self_overlap(texts: list[str]) -> float:
    """Mean pairwise Jaccard of token sets. Higher = more similar (less diverse)."""
    sets = [set(_tokens(t)) for t in texts]
    n = len(sets)
    if n < 2:
        return 0.0
    acc, cnt = 0.0, 0
    for i in range(n):
        for j in range(i + 1, n):
            u = sets[i] | sets[j]
            if u:
                acc += len(sets[i] & sets[j]) / len(u)
                cnt += 1
    return float(acc / cnt) if cnt else 0.0


def token_lengths(texts: list[str]) -> list[int]:
    return [len(_tokens(t)) for t in texts]


def length_matched_indices(lengths: list[int], lo_pct=20, hi_pct=80) -> list[int]:
    """Keep only artifacts whose length is within the central band, killing the length confound."""
    arr = np.array(lengths)
    lo, hi = np.percentile(arr, [lo_pct, hi_pct])
    return [i for i, L in enumerate(lengths) if lo <= L <= hi]
