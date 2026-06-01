"""Convergence Pressure — main experiment runner.

Runs N creators across G generations under four conditions (SOLO, AI_STATIC,
AI_FEEDBACK, AI_DIVERSE) for a fixed task+theme, saving raw artifacts and
per-generation diversity metrics to results/.

Usage:
    python -m src.run --task story --theme "a city that forgets" --n 12 --gens 6
    python -m src.run --task story --all-themes --n 12 --gens 6
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from . import metrics
from .llm import chat, embed
from .personas import ADVISOR_DEFAULT, ADVISORS_DIVERSE, CREATORS
from .tasks import TASKS

GEN_MODEL = "gpt-4o-mini"
EMB_MODEL = "text-embedding-3-small"
TEMP = 1.0
RESULTS = Path(__file__).resolve().parent.parent / "results"

CONDITIONS = ["SOLO", "AI_STATIC", "AI_FEEDBACK", "AI_DIVERSE"]


def creator_solo(persona: str, instruction: str, theme: str, salt: str) -> str:
    msgs = [
        {"role": "system", "content": f"You are {persona}. Write in your own distinctive voice."},
        {"role": "user", "content": f"Theme: {theme}.\n{instruction}"},
    ]
    return chat(msgs, GEN_MODEL, TEMP, salt=salt)


def advisor_suggest(advisor: str, instruction: str, theme: str, trending: list[str] | None, salt: str) -> str:
    sys = f"You are {advisor}."
    user = f"Theme: {theme}.\n{instruction}\nSuggest one strong idea the writer could use."
    if trending:
        examples = "\n".join(f"- {t}" for t in trending)
        user += (
            f"\n\nHere are some popular recent examples other people loved:\n{examples}\n"
            "Suggest an idea in a similar spirit to what is clearly resonating."
        )
    return chat([{"role": "system", "content": sys}, {"role": "user", "content": user}], GEN_MODEL, TEMP, salt=salt)


def creator_with_ai(persona: str, instruction: str, theme: str, suggestion: str, salt: str) -> str:
    msgs = [
        {"role": "system", "content": f"You are {persona}. Write in your own distinctive voice."},
        {
            "role": "user",
            "content": (
                f"Theme: {theme}.\n{instruction}\n\n"
                f"A writing assistant suggests:\n\"{suggestion}\"\n\n"
                "Incorporate the assistant's suggestion into your piece."
            ),
        },
    ]
    return chat(msgs, GEN_MODEL, TEMP, salt=salt)


def run_condition(cond: str, instruction: str, theme: str, n: int, gens: int, rng: np.random.Generator):
    personas = CREATORS[:n]
    history: list[list[str]] = []  # artifacts per generation
    for g in range(gens):
        trending = None
        if cond in ("AI_FEEDBACK", "AI_DIVERSE") and history:
            prev = history[-1]
            k = min(4, len(prev))
            trending = [prev[i] for i in rng.choice(len(prev), size=k, replace=False)]
        artifacts: list[str] = []
        for ci, persona in enumerate(personas):
            salt = f"{cond}:g{g}:c{ci}"
            if cond == "SOLO":
                art = creator_solo(persona, instruction, theme, salt)
            else:
                if cond == "AI_DIVERSE":
                    advisor = ADVISORS_DIVERSE[ci % len(ADVISORS_DIVERSE)]
                else:
                    advisor = ADVISOR_DEFAULT
                use_trend = trending if cond in ("AI_FEEDBACK", "AI_DIVERSE") else None
                sug = advisor_suggest(advisor, instruction, theme, use_trend, salt + ":adv")
                art = creator_with_ai(persona, instruction, theme, sug, salt)
            artifacts.append(art)
        history.append(artifacts)
        print(f"  [{cond}] gen {g+1}/{gens} done ({len(artifacts)} artifacts)")
    return history


def compute_metrics(history: list[list[str]], global_mean: np.ndarray):
    per_gen = []
    for g, arts in enumerate(history):
        emb = embed(arts, EMB_MODEL)
        emb_c = metrics.center(emb, global_mean)
        lengths = metrics.token_lengths(arts)
        lm_idx = metrics.length_matched_indices(lengths)
        rec = {
            "gen": g,
            "n": len(arts),
            "dispersion_raw": metrics.semantic_dispersion(emb),
            "dispersion_centered": metrics.semantic_dispersion(emb_c),
            "dispersion_lenmatched": metrics.semantic_dispersion(emb[lm_idx]) if len(lm_idx) > 2 else None,
            "eff_dim": metrics.participation_ratio(emb_c),
            "distinct2": metrics.distinct_2(arts),
            "self_overlap": metrics.self_overlap(arts),
            "mean_len": float(np.mean(lengths)),
            "std_len": float(np.std(lengths)),
        }
        per_gen.append(rec)
    return per_gen


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", default="story", choices=list(TASKS.keys()))
    ap.add_argument("--theme", default=None)
    ap.add_argument("--all-themes", action="store_true")
    ap.add_argument("--n", type=int, default=12)
    ap.add_argument("--gens", type=int, default=6)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--conditions", nargs="*", default=CONDITIONS)
    args = ap.parse_args()

    task = TASKS[args.task]
    themes = task["themes"] if args.all_themes else [args.theme or task["themes"][0]]
    RESULTS.mkdir(exist_ok=True)

    for theme in themes:
        rng = np.random.default_rng(args.seed)
        print(f"\n=== task={args.task} theme={theme!r} n={args.n} gens={args.gens} ===")
        out = {
            "meta": {
                "task": args.task,
                "theme": theme,
                "instruction": task["instruction"],
                "n": args.n,
                "gens": args.gens,
                "seed": args.seed,
                "gen_model": GEN_MODEL,
                "emb_model": EMB_MODEL,
                "temperature": TEMP,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            "conditions": {},
        }
        # Pass 1: generate all artifacts for every condition.
        histories: dict[str, list[list[str]]] = {}
        for cond in args.conditions:
            print(f"-- condition {cond}")
            histories[cond] = run_condition(
                cond, task["instruction"], theme, args.n, args.gens, np.random.default_rng(args.seed)
            )
        # Run-global mean over every artifact, for the anisotropy-centered metric.
        all_texts = [a for hist in histories.values() for gen in hist for a in gen]
        gmean = metrics.global_mean(embed(all_texts, EMB_MODEL))
        # Pass 2: metrics per condition against the shared global mean.
        for cond in args.conditions:
            per_gen = compute_metrics(histories[cond], gmean)
            out["conditions"][cond] = {"artifacts": histories[cond], "metrics": per_gen}
        slug = theme.replace(" ", "_").replace("'", "")
        path = RESULTS / f"run_{args.task}_{slug}.json"
        path.write_text(json.dumps(out, ensure_ascii=False, indent=2))
        print(f"saved -> {path}")


if __name__ == "__main__":
    main()
