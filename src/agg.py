"""Aggregate the per-theme runs into the headline statistics.

For each condition: the three per-theme slopes of centered dispersion vs generation,
their mean, a one-sample t-test vs 0 (does this condition decline?), and the mean
normalized endpoint (gen-5 dispersion / gen-0), i.e. how much variety is left.
Uses the metrics already stored in each run JSON (no API calls)."""
from __future__ import annotations

import glob
import json
from pathlib import Path

import numpy as np
from scipy import stats as st  # type: ignore

ROOT = Path(__file__).resolve().parent.parent
CONDS = ["SOLO", "AI_STATIC", "AI_FEEDBACK", "AI_DIVERSE"]
KEY = "dispersion_centered"


def main():
    runs = [json.load(open(p)) for p in sorted(glob.glob(str(ROOT / "results" / "run_story_*.json")))]
    print(f"themes aggregated: {len(runs)}\n")
    print(f"{'condition':<13}{'slopes (per theme)':<30}{'mean slope':>11}{'t vs 0':>9}{'p':>8}{'end/gen0':>10}")
    print("-" * 81)
    summary = {}
    for c in CONDS:
        slopes, endpoints = [], []
        for r in runs:
            ms = r["conditions"][c]["metrics"]
            y = np.array([m[KEY] for m in sorted(ms, key=lambda m: m["gen"])])
            x = np.arange(len(y))
            sl = st.linregress(x, y).slope
            slopes.append(sl)
            endpoints.append(y[-1] / y[0])
        slopes = np.array(slopes)
        t, p = st.ttest_1samp(slopes, 0.0)
        end = float(np.mean(endpoints))
        summary[c] = dict(slopes=slopes.tolist(), mean_slope=float(slopes.mean()), t=float(t), p=float(p), end_ratio=end)
        sl_str = " ".join(f"{s:+.4f}" for s in slopes)
        print(f"{c:<13}{sl_str:<30}{slopes.mean():>+11.4f}{t:>9.2f}{p:>8.3f}{end:>10.3f}")
    print()
    # Drop relative to SOLO endpoint
    base = summary["SOLO"]["end_ratio"]
    for c in CONDS:
        drop = (1 - summary[c]["end_ratio"]) * 100
        print(f"  {c:<13} variety retained at gen5 = {summary[c]['end_ratio']*100:.1f}%  (lost {drop:.1f}%)")
    (ROOT / "results" / "summary.json").write_text(json.dumps(summary, indent=2))
    print("\nwrote results/summary.json")


if __name__ == "__main__":
    main()
