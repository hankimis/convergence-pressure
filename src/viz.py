"""Render the headline figures from results/run_*.json.

Outputs to paper/figs/:
  fig1_dispersion.png   - semantic dispersion (anisotropy-centered) vs generation, per condition
  fig1_dispersion.gif   - same, animated generation-by-generation (README money shot)
  fig3_effdim.png       - effective dimensionality collapse
  fig4_confound.png     - raw vs centered vs length-matched dispersion (effect survives confounds)

Aggregates across every run_*.json present (mean over themes; band = min/max).
"""
from __future__ import annotations

import glob
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.animation as animation  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
FIGS = ROOT / "paper" / "figs"
FIGS.mkdir(parents=True, exist_ok=True)

COND_ORDER = ["SOLO", "AI_STATIC", "AI_FEEDBACK", "AI_DIVERSE"]
COND_LABEL = {
    "SOLO": "Solo (no AI)",
    "AI_STATIC": "AI-assisted (no memory)",
    "AI_FEEDBACK": "AI-assisted (reflective loop)",
    "AI_DIVERSE": "Reflective + diverse advisors",
}
COND_COLOR = {
    "SOLO": "#2a7f3f",
    "AI_STATIC": "#c9962a",
    "AI_FEEDBACK": "#c0392b",
    "AI_DIVERSE": "#2e6fb0",
}

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "figure.dpi": 130,
})


def load_runs():
    runs = [json.load(open(p)) for p in sorted(glob.glob(str(ROOT / "results" / "run_*.json")))]
    if not runs:
        raise SystemExit("no results/run_*.json found - run src.run first")
    return runs


def series(runs, cond: str, key: str, normalize: bool = False):
    """Return (gens, mean, lo, hi) aggregated over runs for one condition+metric.

    normalize=True divides each run's series by its own gen-0 value before pooling,
    so theme-level baseline differences cancel and the curves show *relative* decay.
    Bands span min..max across runs (or +/- SEM when many runs)."""
    per_run: list[list[float]] = []
    for r in runs:
        c = r["conditions"].get(cond)
        if not c:
            continue
        vals = {m["gen"]: m.get(key) for m in c["metrics"] if m.get(key) is not None}
        gens = sorted(vals)
        arr = np.array([vals[g] for g in gens], dtype=float)
        if normalize and arr[0] != 0:
            arr = arr / arr[0]
        per_run.append(arr)
    M = np.vstack(per_run)
    gens = np.arange(M.shape[1])
    mean = M.mean(axis=0)
    if M.shape[0] >= 3:
        sem = M.std(axis=0, ddof=1) / np.sqrt(M.shape[0])
        lo, hi = mean - sem, mean + sem
    else:
        lo, hi = M.min(axis=0), M.max(axis=0)
    return gens, mean, lo, hi


def _style_ax(ax, ylabel, title):
    ax.set_xlabel("Generation")
    ax.set_ylabel(ylabel)
    ax.set_title(title, fontsize=12, weight="bold")
    ax.grid(True, alpha=0.25)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def fig_dispersion(runs):
    norm = len(runs) > 1  # normalize to gen-0 only when aggregating multiple runs
    ylab = "Relative semantic dispersion (vs gen 0)" if norm else "Semantic dispersion (centered cosine)"
    band = f"band = ±SEM across {len(runs)} themes" if len(runs) >= 3 else None
    title = "Cultural convergence under AI mediation"
    if band:
        title += f"\n{band}"
    fig, ax = plt.subplots(figsize=(8, 5))
    for cond in COND_ORDER:
        if cond not in runs[0]["conditions"]:
            continue
        g, mean, lo, hi = series(runs, cond, "dispersion_centered", normalize=norm)
        ax.plot(g, mean, "-o", color=COND_COLOR[cond], lw=2.3, label=COND_LABEL[cond], ms=5)
        if len(runs) > 1:
            ax.fill_between(g, lo, hi, color=COND_COLOR[cond], alpha=0.13)
    if norm:
        ax.axhline(1.0, color="#888", lw=0.8, ls=":")
    _style_ax(ax, ylab, title)
    ax.legend(frameon=False, fontsize=9, loc="best")
    fig.tight_layout()
    fig.savefig(FIGS / "fig1_dispersion.png")
    print("wrote fig1_dispersion.png")

    # Animated reveal for README.
    g0, _, _, _ = series(runs, COND_ORDER[0], "dispersion_centered", normalize=norm)
    data = {c: series(runs, c, "dispersion_centered", normalize=norm) for c in COND_ORDER if c in runs[0]["conditions"]}
    fig2, ax2 = plt.subplots(figsize=(8, 5))
    _style_ax(ax2, ylab, "Cultural convergence under AI mediation")
    allv = np.concatenate([d[1] for d in data.values()])
    ax2.set_xlim(g0.min(), g0.max())
    ax2.set_ylim(allv.min() * 0.9, allv.max() * 1.05)
    lines = {c: ax2.plot([], [], "-o", color=COND_COLOR[c], lw=2.3, label=COND_LABEL[c], ms=5)[0] for c in data}
    ax2.legend(frameon=False, fontsize=9, loc="best")

    def frame(i):
        for c, (g, mean, _, _) in data.items():
            lines[c].set_data(g[: i + 1], mean[: i + 1])
        return list(lines.values())

    ani = animation.FuncAnimation(fig2, frame, frames=len(g0), interval=600, blit=True)
    ani.save(FIGS / "fig1_dispersion.gif", writer=animation.PillowWriter(fps=2))
    print("wrote fig1_dispersion.gif")


def fig_effdim(runs):
    fig, ax = plt.subplots(figsize=(8, 5))
    for cond in COND_ORDER:
        if cond not in runs[0]["conditions"]:
            continue
        g, mean, lo, hi = series(runs, cond, "eff_dim")
        ax.plot(g, mean, "-o", color=COND_COLOR[cond], lw=2.3, label=COND_LABEL[cond], ms=5)
        if len(runs) > 1:
            ax.fill_between(g, lo, hi, color=COND_COLOR[cond], alpha=0.12)
    _style_ax(ax, "Effective dimensionality (participation ratio)", "How many directions the population still occupies")
    ax.legend(frameon=False, fontsize=9, loc="best")
    fig.tight_layout()
    fig.savefig(FIGS / "fig3_effdim.png")
    print("wrote fig3_effdim.png")


def fig_confound(runs):
    fig, ax = plt.subplots(figsize=(8, 5))
    cond = "AI_FEEDBACK"
    for key, ls, lab in [
        ("dispersion_raw", "--", "raw cosine"),
        ("dispersion_centered", "-", "anisotropy-centered"),
        ("dispersion_lenmatched", ":", "length-matched"),
    ]:
        g, mean, _, _ = series(runs, cond, key)
        ax.plot(g, mean, ls, marker="o", lw=2.2, label=lab, ms=4)
    _style_ax(ax, "Semantic dispersion", "Collapse survives confound controls (AI reflective loop)")
    ax.legend(frameon=False, fontsize=9)
    fig.tight_layout()
    fig.savefig(FIGS / "fig4_confound.png")
    print("wrote fig4_confound.png")


def fig_scissors(runs):
    """Quality (up) vs diversity (down) across conditions: the Doshi-Hauser scissors."""
    if "quality" not in runs[0]["conditions"].get(COND_ORDER[0], {}):
        print("skip fig2_scissors (no quality scores yet; run src.score)")
        return
    conds = [c for c in COND_ORDER if c in runs[0]["conditions"]]
    qual, disp = [], []
    for c in conds:
        qv = [np.mean([q["mean_adj"] for q in r["conditions"][c]["quality"]]) for r in runs]
        dv = [np.mean([m["dispersion_centered"] for m in r["conditions"][c]["metrics"]]) for r in runs]
        qual.append(np.mean(qv))
        disp.append(np.mean(dv))
    x = np.arange(len(conds))
    fig, ax1 = plt.subplots(figsize=(8, 5))
    bars = ax1.bar(x, qual, width=0.5, color="#c9962a", alpha=0.75, label="Individual quality (length-adj.)")
    ax1.set_ylabel("Mean individual quality (length-adjusted)", color="#9a6f12")
    ax1.set_ylim(min(qual) * 0.96, max(qual) * 1.02)
    ax1.set_xticks(x)
    ax1.set_xticklabels([COND_LABEL[c] for c in conds], rotation=15, ha="right", fontsize=8)
    ax2 = ax1.twinx()
    ax2.plot(x, disp, "-o", color="#c0392b", lw=2.5, ms=7, label="Population diversity (dispersion)")
    ax2.set_ylabel("Population semantic dispersion", color="#c0392b")
    ax1.set_title("The scissors: individual quality up, collective diversity down", fontsize=12, weight="bold")
    for s in ("top",):
        ax1.spines[s].set_visible(False)
        ax2.spines[s].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIGS / "fig2_scissors.png")
    print("wrote fig2_scissors.png")


if __name__ == "__main__":
    runs = load_runs()
    fig_dispersion(runs)
    fig_scissors(runs)
    fig_effdim(runs)
    fig_confound(runs)
