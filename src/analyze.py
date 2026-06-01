"""Offline analysis from cached artifacts: trend slopes, and length-matched
CENTERED dispersion (to test whether the centered-cosine collapse survives the
length confound). Re-embeds from cache, so no new API spend."""
from __future__ import annotations

import glob
import json
from pathlib import Path

import numpy as np
from scipy import stats as _stats  # type: ignore

from . import metrics
from .llm import embed

ROOT = Path(__file__).resolve().parent.parent
EMB = "text-embedding-3-small"
CONDS = ["SOLO", "AI_STATIC", "AI_FEEDBACK", "AI_DIVERSE"]


def linfit(y):
    x = np.arange(len(y))
    sl, inter, r, p, se = _stats.linregress(x, y)
    return sl, r, p


def analyze(path):
    d = json.load(open(path))
    # run-global mean over all artifacts
    all_texts = [a for c in CONDS for gen in d["conditions"][c]["artifacts"] for a in gen]
    gmean = embed(all_texts, EMB).mean(axis=0)
    print(f"\n=== {Path(path).name}  (n={d['meta']['n']}, gens={d['meta']['gens']}) ===")
    print(f"{'cond':<12}{'disp_ctr slope':>16}{'r':>7}{'p':>8}   {'lenmatched-centered by gen':>30}")
    rows = {}
    for c in CONDS:
        arts = d["conditions"][c]["artifacts"]
        ctr_series, lmctr_series = [], []
        for gen in arts:
            emb = embed(gen, EMB)
            embc = metrics.center(emb, gmean)
            ctr_series.append(metrics.semantic_dispersion(embc))
            lengths = metrics.token_lengths(gen)
            idx = metrics.length_matched_indices(lengths)
            lmctr_series.append(metrics.semantic_dispersion(embc[idx]) if len(idx) > 2 else float("nan"))
        sl, r, p = linfit(ctr_series)
        rows[c] = dict(ctr=ctr_series, lmctr=lmctr_series, slope=sl, r=r, p=p)
        lm = " ".join(f"{v:.3f}" for v in lmctr_series)
        print(f"{c:<12}{sl:>16.4f}{r:>7.2f}{p:>8.3f}   {lm:>30}")
    return rows


if __name__ == "__main__":
    for p in sorted(glob.glob(str(ROOT / "results" / "run_*.json"))):
        analyze(p)
