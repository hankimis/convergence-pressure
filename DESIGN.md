# Convergence Pressure, Study Design

> Does putting a generative model in the creative loop collapse the *diversity* of what a population of creators produces, even when it raises the quality of each individual?
>
> IOV LABS. Status: **own experiment, in progress.** This document is the pre-registration: hypotheses, conditions, metrics, and confound controls are fixed here *before* the headline numbers are read.

## 1. Thesis under test

The reported phenomenon is a scissors: generative AI **raises individual creativity** while **lowering collective diversity**. Writers given AI plot ideas write better stories, but their stories look more like each other (Doshi & Hauser 2024). We restate this as a dynamical claim and test it directly:

> **When a shared model mediates an iterated creative process, the semantic diversity of the population's output decays over generations toward a low-dimensional attractor. The decay is faster when the model is conditioned on the population's own recent output (a feedback loop), and it is partially reversible by injecting model-level diversity.**

Two things make this more than a restatement:

1. **A generational feedback loop.** Prior work measures one-shot homogenization. The interesting regime is the loop: the model's suggestions in generation *t* are conditioned on what the population produced in generation *t−1* (the model reflects the crowd back at itself). This is the mechanism behind "model collapse" on synthetic-data diets (Shumailov et al. 2024), here transplanted into a *human-in-the-loop cultural* setting rather than a pure retraining setting.
2. **An information-theoretic diversity measure with confound controls**, not a vibe. We report semantic dispersion *and* effective dimensionality *and* lexical diversity, length-matched, against a no-AI baseline.

## 2. What would falsify it

- **H1 (collapse).** Semantic dispersion `D_t` declines monotonically in the AI conditions and is flat (within noise) in the solo condition. *Falsified if* the AI condition's `D_t` is statistically indistinguishable from solo, or does not decline.
- **H2 (feedback accelerates).** `D_t` declines faster (steeper slope, lower asymptote) in **AI-feedback** than in **AI-static**. *Falsified if* feedback ≈ static.
- **H3 (reversibility).** A **diverse-personas** intervention raises the asymptotic `D_∞` relative to AI-feedback. *Falsified if* the intervention does not lift the curve.
- **H4 (quality–diversity scissors).** Mean individual *quality* (rated) is ≥ solo in the AI conditions while *diversity* is lower, the two move in opposite directions. *Falsified if* quality drops with diversity (then it is just degradation, not a scissors).

We keep negative results. If H1 fails, that is the paper.

## 3. Design

A population of `N` creators produces an artifact each generation for `G` generations, under four conditions. Conditions share the **same personas and the same theme** (paired), so any difference is the AI's doing.

### Conditions

| Code | Name | Per-creator step | Loop? |
|---|---|---|---|
| `SOLO` | Solo (control) | persona writes alone | no AI |
| `AI_STATIC` | AI-assisted, no memory | one fixed AI advisor suggests; persona incorporates | AI does **not** see prior gens |
| `AI_FEEDBACK` | AI-assisted, reflective | AI advisor is shown a sample of **gen t−1** outputs as "what's trending," then suggests | **yes**, the runaway loop |
| `AI_DIVERSE` | Feedback + diverse advisors | same loop, but `K` distinct advisor personas, one sampled per creator | yes, with diversity injection |

`SOLO` bounds the natural drift of an unaided population. `AI_STATIC` isolates "AI in the loop at all." `AI_FEEDBACK` adds the reflective loop. `AI_DIVERSE` tests the mitigation (Wan & Kalman 2026, diverse AI personas).

### The creative task

Fixed-theme, open-form generation that admits genuine semantic variety. Default: **invent a concept for a short story** (2–3 sentences) on a fixed theme (e.g., *"a city that forgets"*). Swappable tasks (startup pitch, metaphor, melody-in-words) live in `tasks.py` so the result is shown not to hinge on one task.

## 4. Metrics

All embeddings via `text-embedding-3-small` (dated snapshot recorded in results).

- **Semantic dispersion** `D_t` = mean pairwise cosine **distance** of the gen-*t* artifact embeddings. The headline curve.
- **Effective dimensionality** `EDim_t` = exp(entropy of normalized PCA eigenvalues), how many independent "directions" the population still occupies. Collapse = falling EDim.
- **Lexical diversity**: distinct-2 and self-BLEU, to separate *semantic* convergence from mere wording overlap.
- **Quality** (for H4): a held-out LLM judge rates each artifact 1–10 on originality+craft, blind to condition. (We know LLM judges favor length, see our own `llm-judge-bench`, so quality is **length-controlled**, below.)

## 5. Confound controls (the part that makes it real)

1. **Length confound.** AI may homogenize *length*, which deflates both dispersion and quality. We log token length per artifact and (a) report length distributions per condition, (b) re-compute `D_t` on **length-matched** subsamples, (c) length-residualize the quality score. Report before-vs-after.
2. **Temperature held constant** (= 1.0) across every generating call, every condition. A separate temperature sweep checks the curve is not an artifact of one setting.
3. **Embedding-anisotropy confound.** Raw `text-embedding-3` space is anisotropic, which inflates baseline similarity. We **center and whiten** embeddings on the gen-0 pooled set before computing distances, and report raw vs whitened.
4. **Judge confound.** Quality uses a *different* model family than the generator where possible; ratings are blind to condition and order-shuffled.
5. **Population-size & theme robustness.** Re-run at two `N` and ≥3 themes; the claim must survive aggregation, not cherry-pick.
6. **Seed/snapshot reproducibility.** Fixed RNG seed for all sampling; model snapshot IDs and date pinned in `results/meta.json`; one-command `make run`.

## 6. Planned figures

- **Fig 1 (money shot).** `D_t` vs generation, one line per condition, CI bands: SOLO flat on top, AI_STATIC sagging, AI_FEEDBACK collapsing, AI_DIVERSE recovering between. Animated reveal generation-by-generation for the README GIF.
- **Fig 2.** The scissors: individual quality (↑) vs population diversity (↓) on twin axes for the AI conditions.
- **Fig 3.** Effective dimensionality collapse + a 2-D PCA scatter of gen-0 vs gen-G clouds (the cloud visibly shrinking).
- **Fig 4.** Confound panel: raw vs length-matched vs whitened `D_t` (showing the effect survives).

## 7. Epistemics / philosophy section (paper)

Reserved, but the spine: Mill's *On Liberty* argument that truth needs a diversity of error to stay alive; cultural-evolution monoculture and fragility; **value lock-in** (Bostrom; MacAskill) as the long-run stake; Goodhart and the map-vs-territory caveat that *a diversity metric is not diversity*, a population can score high on cosine dispersion while being culturally flat, and vice-versa. The honest claim is narrow: *under this operationalization*, mediation compresses the measured variety, and that is evidence about, not proof of, the cultural worry.

## 8. References (to verify in paper)

- Doshi & Hauser 2024, *Generative AI Enhances Individual Creativity but Reduces the Collective Diversity of Novel Content* (Science Advances).
- Shumailov et al. 2024, *AI models collapse when trained on recursively generated data* (Nature).
- Wan & Kalman 2026, *Diverse AI Personas Can Mitigate the Homogenization Effect in Human-AI Collaborative Ideation* (arXiv:2504.13868).
- Padmakumar & He 2024, *Does Writing with Language Models Reduce Content Diversity?* (ICLR; arXiv:2309.05196).
- Mill, *On Liberty* (1859); Bostrom, *Superintelligence* (2014); MacAskill, *What We Owe the Future* (2022).
