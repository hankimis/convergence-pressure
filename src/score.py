"""Quality scoring for the quality-diversity scissors (H4).

A cross-family judge (Claude) rates every artifact 1-10 for originality + craft,
blind to condition. Scores are length-residualized (we know judges favor length)
and aggregated per condition. Writes scores back into each run JSON under
conditions[cond]['quality'].
"""
from __future__ import annotations

import glob
import json
import re
from pathlib import Path

import numpy as np

from .llm import claude_judge
from .metrics import token_lengths

ROOT = Path(__file__).resolve().parent.parent
CONDS = ["SOLO", "AI_STATIC", "AI_FEEDBACK", "AI_DIVERSE"]

PROMPT = (
    "You are a literary judge. Rate the following short creative piece for ORIGINALITY and "
    "CRAFT on an integer scale from 1 (derivative, weak) to 10 (strikingly original, masterful). "
    "Judge only the writing, ignore length. Output ONLY the integer.\n\nPIECE:\n\"\"\"\n{txt}\n\"\"\""
)


def rate(text: str) -> float:
    out = claude_judge(PROMPT.format(txt=text))
    m = re.search(r"\d+", out)
    if not m:
        return float("nan")
    return float(min(10, max(1, int(m.group()))))


def residualize(scores: np.ndarray, lengths: np.ndarray) -> np.ndarray:
    """Remove the linear length component so quality is not just 'longer = better'."""
    ok = ~np.isnan(scores)
    if ok.sum() < 3:
        return scores
    x, y = lengths[ok], scores[ok]
    A = np.vstack([x, np.ones_like(x)]).T
    sl, inter = np.linalg.lstsq(A, y, rcond=None)[0]
    resid = scores - (sl * lengths + inter)
    return resid + np.nanmean(scores)  # re-center to original scale


def score_run(path: str):
    d = json.load(open(path))
    print(f"\n=== scoring {Path(path).name} ===")
    # flat list for a single global length residualization
    flat = []  # (cond, gen, idx, text)
    for c in CONDS:
        for g, gen in enumerate(d["conditions"][c]["artifacts"]):
            for i, t in enumerate(gen):
                flat.append((c, g, i, t))
    raw = np.array([rate(t) for *_, t in flat])
    lens = np.array(token_lengths([t for *_, t in flat]), dtype=float)
    adj = residualize(raw, lens)
    # regroup per condition/gen
    for c in CONDS:
        per_gen_raw: dict[int, list[float]] = {}
        per_gen_adj: dict[int, list[float]] = {}
        for k, (cc, g, i, t) in enumerate(flat):
            if cc != c:
                continue
            per_gen_raw.setdefault(g, []).append(raw[k])
            per_gen_adj.setdefault(g, []).append(adj[k])
        gens = sorted(per_gen_raw)
        d["conditions"][c]["quality"] = [
            {
                "gen": g,
                "mean_raw": float(np.nanmean(per_gen_raw[g])),
                "mean_adj": float(np.nanmean(per_gen_adj[g])),
            }
            for g in gens
        ]
        ov = float(np.nanmean(raw[[k for k, (cc, *_2) in enumerate(flat) if cc == c]]))
        print(f"  {c:<12} overall raw quality = {ov:.2f}")
    json.dump(d, open(path, "w"), ensure_ascii=False, indent=2)
    print(f"  saved scores -> {path}")


if __name__ == "__main__":
    for p in sorted(glob.glob(str(ROOT / "results" / "run_*.json"))):
        score_run(p)
