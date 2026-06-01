#set document(title: "Convergence Pressure", author: "Han Kim")
#set page(
  paper: "a4",
  margin: (x: 2.2cm, y: 2.4cm),
  numbering: "1",
)
#set text(font: ("Libertinus Serif", "AppleMyungjo"), size: 10.5pt)
#set par(justify: true, leading: 0.62em)
#show heading: set block(above: 1.2em, below: 0.7em)
#set heading(numbering: "1.1")

#align(center)[
  #text(17pt, weight: "bold")[Convergence Pressure]
  #v(2pt)
  #text(12pt)[Measuring AI-Mediated Cultural Homogenization in Iterated Creation]
  #v(8pt)
  #text(10.5pt)[Han Kim]
  #v(1pt)
  #text(9pt)[IOV Labs (아이오브연구소) · #link("mailto:hankim@iovstudio.kr")[hankim\@iovstudio.kr] · ORCID 0009-0000-5998-1358]
  #v(2pt)
  #text(9pt, style: "italic")[Draft, June 2026]
]

#v(6pt)

#align(center)[#block(width: 86%, inset: 8pt, stroke: 0.5pt + luma(170), radius: 4pt)[
  #set text(9.5pt)
  #set par(justify: true)
  *Abstract.* Generative AI raises the creativity of an individual while lowering the
  diversity of the crowd (Doshi & Hauser, 2024); models retrained on their own output
  collapse (Shumailov et al., 2024). We join the two into one dynamical question: when a
  shared model mediates an *iterated* creative process, does a population's semantic
  diversity decay over generations, and what drives it? We run a controlled,
  reproducible experiment in which a fixed pool of diverse creator personas produces one
  artifact per generation under four conditions: writing alone, writing with a static AI
  advisor, writing with an advisor that reflects the population's own recent output back
  at it, and the same reflective loop with a panel of diverse advisors. The headline result
  is a *dissociation*: AI assistance _per se_ leaves population diversity flat ($100$–$102%$
  retained over six generations), but the *reflective loop*, the AI echoing the crowd's
  recent hits, drives an anisotropy-controlled decline of about $10$–$12%$. The obvious fix
  fails: a panel of *diverse* AI advisors, which preserves variety in a single round, does
  *not* prevent the collapse under iteration (it loses slightly more). We report the effect
  under length-matching and anisotropy controls, keep the metric-dependence and this
  negative result in view, and close with a philosophical account of why a contracting
  measure of variety is evidence about, not proof of, a cultural monoculture.
]]

= Introduction

The motivating tension is now well documented at the level of a *single* interaction.
Doshi and Hauser @doshi2024generative gave writers access to generative-AI story ideas
and found a scissors: individual stories were rated more creative and better written,
yet the set of stories became *more similar to one another*. Padmakumar and He
@padmakumar2024writing report the same compression of content diversity when people
write with language models. Separately, in the pure-retraining setting, Shumailov et al.
@shumailov2024collapse show that a model trained recursively on its own outputs suffers
*model collapse*: the tails of the distribution thin and then vanish.

These are two halves of one mechanism seen from different sides. The first measures a
*one-shot* human-facing effect; the second measures a *many-generation* machine-facing
effect. The cultural worry that animates public debate, that an AI-saturated culture
slowly converges on a house style, lives in the gap between them: it is a
*many-generation, human-in-the-loop* effect, which neither literature measures directly.
This paper builds an instrument for that gap.

The worry is not new, but its scale is. When a small number of frontier models mediate a large
fraction of the world's writing, design, and image-making, any systematic pull they exert on
creative output is applied to a shared population at once, round after round. A bias that would
be harmless in a single tool becomes a slow current when the same tool sits in millions of loops.
What is missing is not concern but measurement: a way to ask, under controlled conditions, whether
the current exists, what switches it on, and whether the obvious remedies work. That is what this
paper supplies.

We restate the worry as a falsifiable dynamical claim:

#block(inset: (left: 10pt), stroke: (left: 2pt + luma(160)))[
  When a shared model mediates an iterated creative process, the semantic dispersion of a
  creator population decays over generations toward a low-dimensional attractor; the decay
  is faster when the model is conditioned on the population's own recent output (a
  reflective feedback loop), and it is partly reversible by injecting model-level
  diversity.
]

Our contribution is threefold. (1) A *controlled, paired* design that separates "AI in
the loop at all" from "AI reflecting the crowd," so the cause of any homogenization is
identified rather than assumed. (2) An *anisotropy- and length-controlled* diversity
measurement, with the confounds removed by construction rather than waved away. (3) An
honest, reproducible artifact: seeds and model snapshots are pinned, generations are
content-cached, and negative and metric-dependent results are reported rather than hidden.

= Related work

*Individual gain, collective loss.* @doshi2024generative and @padmakumar2024writing
establish the one-shot scissors for human writers. Our design imports their finding and
asks what it does *over time* when the outputs feed back into the next round's prompting.

*Model collapse.* @shumailov2024collapse formalize the degenerative dynamics of training
on synthetic data. Our reflective condition is the cultural analogue: rather than a model
retraining on its outputs, a *population* is repeatedly nudged by an advisor that has seen
the population's recent hits. No weights are updated; the loop runs entirely in context.

*Mitigations.* Wan and Kalman @wan2026diverse show that assigning *diverse* AI personas
preserves variety in collaborative ideation. We test this as an intervention arm and
measure how much of the collapse it arrests.

= Method

== Population and task

A pool of $N$ creator personas, deliberately varied along tradition, temperament, era, and
register (a terse Scandinavian crime novelist; a Nigerian Afrofuturist; a Kafkaesque
clerk; a cyberpunk street poet; and so on), each produce one short artifact per generation
on a *fixed theme*. Holding the theme and the personas constant across conditions makes the
comparison *paired*: any divergence between conditions is attributable to the AI's role,
not to a different population or prompt. Generation uses #raw("gpt-4o-mini") at temperature
$1.0$; embeddings use #raw("text-embedding-3-small"). Themes and tasks are swappable
(short-story concept, single metaphor, startup pitch) to show the result does not hinge on
one prompt.

== Conditions

#table(
  columns: (auto, 1fr, auto),
  inset: 5pt,
  align: (left, left, center),
  stroke: 0.4pt + luma(180),
  table.header([*Condition*], [*Per-creator step*], [*Reflective loop*]),
  [SOLO], [persona writes alone], [no AI],
  [AI\_STATIC], [a fixed advisor suggests an idea; persona incorporates it], [no],
  [AI\_FEEDBACK], [advisor is shown a sample of generation $t{-}1$ outputs as "what is trending," then suggests; persona incorporates], [*yes*],
  [AI\_DIVERSE], [the reflective loop, but with $K$ distinct advisor personas, one per creator], [yes, diversity injected],
)

SOLO bounds the natural sampling drift of an unaided population. AI\_STATIC isolates the
effect of an AI being in the loop at all, with no memory of the crowd. AI\_FEEDBACK adds
the reflective loop that is our object of study. AI\_DIVERSE tests the mitigation.

== Metrics

Let $E_t = {e_1, ..., e_N}$ be the unit-normalized embeddings of generation $t$.

- *Semantic dispersion* $D_t = frac(2, N(N-1)) sum_(i<j) (1 - cos(e_i, e_j))$, the mean
  pairwise cosine distance. Higher means more diverse. This is the headline.
- *Effective dimensionality* (participation ratio) $"PR"_t = (sum_k lambda_k)^2 \/ sum_k lambda_k^2$
  over the covariance eigenvalues $lambda_k$, how many independent directions the
  population still occupies.
- *Lexical diversity*: distinct-2 and mean pairwise token-set overlap, to separate
  *semantic* convergence from mere wording overlap.

== Confound controls

The credibility of a diversity result rests entirely on the controls.

+ *Embedding anisotropy.* Raw #raw("text-embedding-3") space has a dominant common
  direction that inflates every cosine similarity. We subtract a run-global mean vector
  ("all-but-the-mean") before computing distances, and report raw versus centered. We
  deliberately *do not* full-whiten: estimating a $1536 times 1536$ covariance from $~12$
  points is rank-deficient and maps the points onto a regular simplex, which would
  *manufacture* a constant dispersion. Mean-centering needs only one shared vector and is
  non-degenerate.
+ *Length.* An advisor can homogenize *length*, which mechanically deflates dispersion. We
  log token lengths, recompute dispersion on length-matched central-band subsamples, and
  report before-versus-after.
+ *Temperature* is held at $1.0$ on every generating call, every condition.
+ *Reproducibility.* All sampling is seeded; model snapshot IDs and dates are pinned;
  generations are content-cached so a re-run reproduces the same artifacts.

= Results

We ran $N=12$ creators for $G=6$ generations across three themes ("a city that forgets,"
"the last lighthouse," "an inherited debt"), all four conditions, paired on personas and
theme. For each theme we fit the slope of centered semantic dispersion against generation;
@tab-main reports the three per-theme slopes, their mean, a one-sample $t$-test against
zero, and the variety retained at the final generation (gen-5 dispersion as a fraction of
gen-0).

#figure(
  table(
    columns: (auto, auto, auto, auto, auto),
    inset: 5pt,
    align: (left, center, center, center, center),
    stroke: 0.4pt + luma(180),
    table.header([*Condition*], [*Mean slope*], [*t vs 0*], [*p*], [*Variety retained (gen 5)*]),
    [Solo (no AI)], [$+0.0015$], [$1.06$], [$0.40$], [$100.4%$],
    [AI static (no memory)], [$+0.0025$], [$0.71$], [$0.55$], [$102.0%$],
    [AI reflective loop], [$-0.0237$], [$-3.74$], [$0.065$], [$89.7%$],
    [Reflective + diverse advisors], [$-0.0208$], [$-11.99$], [$bold(0.007)$], [$88.5%$],
  ),
  caption: [Centered-dispersion slope by condition, aggregated over three themes ($n=3$
    slopes per condition). The two non-reflective conditions are flat; both reflective
    conditions decline.],
) <tab-main>

#figure(
  image("figs/fig1_dispersion.png", width: 92%),
  caption: [Relative semantic dispersion versus generation, by condition (mean of three
    themes, band $= plus.minus$SEM). The two non-reflective conditions hold near their
    starting variety; both reflective conditions decay.],
)

*The dissociation (H1, H2).* The result is a clean separation by *mechanism*, not by the
mere presence of AI. Writing alone (slope $+0.0015$, $p=0.40$) and writing with a *static*
AI advisor (slope $+0.0025$, $p=0.55$) both leave the population's variety essentially
unchanged after six generations ($100$–$102%$ retained). The moment the advisor is allowed
to *reflect the crowd*, shown the population's own recent hits and asked to suggest "in a
similar spirit", dispersion declines: the single-advisor reflective loop loses about
$10%$ of its variety (slope $-0.0237$, $p=0.065$), and the effect is directionally present
in every theme. So it is not "AI in the loop" that homogenizes; it is the *feedback*. This
supports H1 and H2.

*The mitigation fails (H3 falsified).* We pre-registered the hopeful hypothesis that a panel
of *diverse* AI advisors would arrest the collapse, following the one-shot ideation result
of Wan and Kalman @wan2026diverse. It does not. Under the iterated loop, diverse advisors
lose $11.5%$ of variety, if anything slightly *more* than the single advisor, with a
strikingly consistent decline across themes (slope $-0.0208$, $t=-11.99$, $p=0.007$). The
intervention that preserves diversity in a single round does not survive repetition: each
generation re-seeds the next round's "trending" set, and even a diverse advisory panel is
pulled toward whatever the population has already converged on. This is the paper's most
important and least comfortable finding, and we report it prominently rather than burying a
null.

*Confounds.* The decline is not an artifact of length: recomputing dispersion on
length-matched central-band subsamples preserves the reflective-loop dip in every theme
(@fig-confound). It is not an artifact of raw embedding anisotropy: the effect is measured
*after* removing the run-global mean, and is in fact masked in raw cosine, where the
dominant common direction inflates similarity. The participation ratio stays roughly flat
($approx 8$–$9$ throughout), so the population *contracts toward an attractor without losing
its nominal dimensionality*, a compression of spread, not a rank collapse. We report this
metric-dependence openly: the convergence lives in the spread of the cloud, not in the count
of directions it occupies.

*The convergence is semantic, not lexical.* This is the sharpest qualification, and it cuts
both ways. Lexical diversity does *not* fall: distinct-2 is essentially unchanged from
generation 0 to 5 in every condition (Solo $0.840 arrow.r 0.842$, reflective loop
$0.858 arrow.r 0.861$), and mean pairwise token overlap is flat or slightly falling. A
researcher measuring homogenization with $n$-gram metrics, the standard cheap tools, would
conclude nothing is happening. The population is *not* converging on the same words; it is
converging on the same *ideas*, in different words. Only a semantic embedding makes the
contraction visible. That is a methodological point in our favour (surface metrics miss this
entirely) and a caution against ours (the contraction is defined in a learned representation
whose geometry is itself a modelling choice; see Limitations).

*Quality moves the other way (H4).* A cross-family judge (Claude, blind to condition,
length-residualized) rates individual artifacts highest in exactly the conditions where
collective diversity is lowest: mean adjusted quality is $5.23$ (Solo), $5.23$ (AI static),
$bold(5.60)$ (reflective loop), $5.49$ (diverse). The reflective loop produces the *best
individual pieces and the least collective variety at once*. This is the Doshi and Hauser
scissors reproduced and sharpened: the homogenizing condition is not a degradation that a
quality filter would catch, it is an *improvement* on every individual axis a writer or a
platform would optimise. That is what makes it dangerous.

#figure(
  image("figs/fig2_scissors.png", width: 88%),
  caption: [The scissors. Individual artifact quality (length-adjusted, cross-family judge)
    against population dispersion, by condition. Quality holds or rises under AI mediation
    while collective diversity falls.],
) <fig-scissors>

#figure(
  image("figs/fig4_confound.png", width: 84%),
  caption: [The reflective-loop decline survives confound controls: raw cosine,
    anisotropy-centered, and length-matched dispersion for the reflective condition.],
) <fig-confound>

= Epistemics and philosophy

== What a falling number can and cannot mean

The instrument measures one thing precisely: the mean pairwise cosine distance of a
population's artifact embeddings, after removing the anisotropic common mode. It is
tempting to read a fall in $D_t$ as "the culture is becoming a monoculture." That reading
is a category error of exactly the kind Goodhart warns against. $D_t$ is a *map*; cultural
variety is the *territory*. A population can score high on cosine dispersion while being
culturally flat (sixteen ways of saying the same fashionable thing, scattered in embedding
space by surface features), and it can score low while being deeply varied (a tight cluster
of profound, mutually irreducible positions). The honest claim is therefore narrow and
conditional: *under this operationalization*, the reflective loop compresses the measured
variety, and that compression is *evidence about*, not proof of, the cultural worry.

== Why diversity is not a luxury

The reason the result matters, if it generalizes, is older than the technology. Mill's
argument in _On Liberty_ @mill1859liberty is that even true beliefs decay into "dead dogma"
without a living diversity of dissent to keep them awake; truth needs error the way a fire
needs air. A culture that converges on a single house style does not merely lose ornament;
it loses the friction that lets it discover it was wrong. The cultural-evolution analogue
is monoculture fragility: a population that has shed its tails has also shed the variation
that adaptation draws on.

The long-run stake is what Bostrom @bostrom2014superintelligence and MacAskill
@macaskill2022what call *value lock-in*: a transition that quietly fixes a civilization's
trajectory before it has finished deliberating. A reflective AI loop is a candidate
lock-in mechanism that needs no malice and no superintelligence, only ubiquity. Each round
it gently re-weights the population toward what already resonated, and the space of what
*could* resonate next contracts. Our experiment is a scale model of that ratchet.

== Why a diverse advisor cannot save the loop

The most counterintuitive result is that diversifying the advisor does not help. The intuition
it violates is reasonable: if homogenization comes from a single voice, surely many voices
should restore variety. Wan and Kalman @wan2026diverse confirm exactly this in a *single*
round. Our finding is that the intuition does not survive iteration, and the reason is
structural rather than incidental. The diversity of the advisor is an input perturbation; the
homogenizing force is a *selection pressure* applied every round, when the advisor is asked to
suggest "in the spirit of what is resonating." A varied set of advisors still reads the same
trending set and is still pulled toward it. Variety injected at the source is washed out by a
filter applied at the sink. In dynamical terms, the loop has an attractor whose location is set
by the feedback rule, not by the richness of the perturbations entering each step; richer
perturbations change the path, not the destination. The practical corollary is uncomfortable for
the dominant alignment instinct: you cannot offset a feedback-driven monoculture by making the
model more diverse if the model is still rewarded, each round, for echoing the crowd. The lever
that matters is the *reflection*, not the *voice*.

== The honest moat

We keep the metric-dependence in view: the effect is clearest in the anisotropy-controlled
dispersion and weaker in raw cosine, and the participation ratio does not collapse, the
population contracts toward an attractor without losing its nominal dimensionality. We keep
the substrate limit in view: these are LLM-simulated creators, so the result is a
*mechanism demonstration*, not a measurement of human culture. The mechanism, a shared
model reflecting the crowd back at itself, is identical to the one at stake in the real
worry; the people are not. Stating both plainly is the point.

= Discussion

== What the dissociation tells a platform designer

The practical reading is specific. A product that drops a static, stateless AI assistant
into a creative tool, one that does not condition on what other users are making, does not,
on this evidence, homogenize its user base. The danger begins precisely with the features
that product teams most want to ship: trending feeds, "popular with creators like you,"
fine-tuning on engagement, retrieval over the platform's own recent hits. Each of these is a
reflective loop. The mechanism we isolate is not exotic; it is the default architecture of a
recommender-shaped creative platform. The contribution is to show that the *loop*, not the
*assistant*, is the active ingredient, and therefore that the mitigation has to act on the
loop.

== Why the field's instinct points the wrong way

The reflexive response to "AI is homogenizing outputs" is "make the AI more diverse", more
personas, higher temperature, broader training data. Our null on the diverse-advisor arm is
evidence that this instinct, while correct for a single interaction, is the wrong lever for a
loop. Diversity at the source is a one-time perturbation; the reflection is a force applied
every round. Fighting a recurring force with a one-time perturbation loses. The levers that
should work are the ones that touch the feedback itself: not showing the model the crowd's
recent hits, injecting novelty pressure that *grows* with convergence rather than staying
constant, or rewarding distance-from-the-corpus directly. We did not test these; they are the
experiments this null makes worth running.

== A minimal model of the loop

The dynamics have a simple closed form that fits what we see. Let each creator $i$ produce, at
generation $t$, an embedding $e_i^t$. Write the population centroid as $mu_t = (1\/N) sum_i e_i^t$.
The reflective advisor samples near the centroid (it echoes "what is trending"), and the creator
incorporates the suggestion, so the next artifact is a convex blend of the creator's own
persona-driven point $p_i$ and a pull toward the centroid:
$ e_i^(t+1) = (1 - alpha) p_i + alpha mu_t + epsilon_i^t, $
where $alpha in [0,1]$ is the strength of the pull and $epsilon_i^t$ is idiosyncratic noise.
Taking variances across the population, the centroid term is shared and contributes nothing to
spread, so the dispersion contracts geometrically toward a persona-residual floor:
$ D_(t) approx D_infinity + (D_0 - D_infinity)(1 - alpha)^t, quad D_infinity prop "Var"(p_i). $
This predicts exactly the shape observed: not a collapse to zero but a decay to a floor set by
how much irreducible persona variance survives the pull. In the static condition there is no
$mu_t$ term ($alpha = 0$) and $D_t$ stays at $D_0$; in the reflective conditions $alpha > 0$ and
$D_t$ falls. Crucially, *the advisor's diversity does not enter $alpha$*: a varied advisory panel
changes which point near $mu_t$ is sampled, not the fact that the pull is toward $mu_t$. That is
the formal reason the diverse-advisor arm collapses too. Estimating $alpha$ per theme from the
fitted slopes gives $alpha approx 0.04$ to $0.07$ per generation, small per round, compounding
over a culture's many rounds.

== Relation to model collapse

Shumailov et al. @shumailov2024collapse describe a degenerative loop in *weight space*: a
model retrained on its own samples loses the tails of its distribution. Ours is the same
shape in *culture space*, with no retraining at all. No gradient is taken; the loop is closed
entirely through context and a population of independent creators. That the same contraction
appears without any parameter update suggests the phenomenon is about *information flow in a
closed loop*, not about the fragility of any particular training procedure, which is both
more general and harder to patch.

= Limitations and future work

*Personas are not people.* The study measures convergence among LLM-simulated creators, so it
is a *mechanism demonstration*, not a measurement of human culture. The mechanism, a shared
model reflecting a population's recent output back at it, is the same one at stake in the real
worry; the substrate is not. Whether human creators, with memory, taste, and contrarian
incentives, damp or amplify the loop is an empirical question this design cannot answer and a
human study could.

*A diversity metric is not diversity.* The convergence is defined as a contraction of cosine
spread in a learned embedding. Because the effect is semantic rather than lexical, it depends
on the embedding's geometry being a faithful map of conceptual variety, which is itself a
modelling assumption. A different encoder could in principle place the same artifacts
differently. We mitigate this by removing the anisotropic common mode and by reporting that the
participation ratio (a different functional of the same space) does not collapse, but the
dependence on a learned representation is real and should be probed with multiple encoders.

*Single model family and short horizon.* Generator and advisor share a model family; a
cross-family loop (one model's outputs steering another's suggestions) may behave differently.
Six generations show a slope, not an asymptote; we cannot yet say whether the curve levels off,
reaches a floor, or keeps falling. Longer horizons, more themes and tasks, additional seeds for
tighter intervals, a temperature sweep, and the loop-breaking interventions named in the
Discussion are the natural next experiments. All negative and metric-dependent results above are
reported, not hidden; that is the point of the artifact.

= Appendix: per-theme slopes

The aggregate in @tab-main pools three themes. For transparency, the underlying per-theme
slopes of centered dispersion against generation are below. The two non-reflective conditions
scatter around zero; the two reflective conditions are negative in every theme.

#figure(
  table(
    columns: (auto, auto, auto, auto),
    inset: 5pt,
    align: (left, center, center, center),
    stroke: 0.4pt + luma(180),
    table.header([*Condition*], [*city forgets*], [*last lighthouse*], [*inherited debt*]),
    [Solo], [$+0.0033$], [$-0.0012$], [$+0.0023$],
    [AI static], [$-0.0003$], [$+0.0096$], [$-0.0017$],
    [AI reflective loop], [$-0.0359$], [$-0.0145$], [$-0.0208$],
    [Reflective + diverse], [$-0.0215$], [$-0.0233$], [$-0.0174$],
  ),
  caption: [Per-theme centered-dispersion slopes. Every reflective-condition cell is negative;
    no non-reflective cell is consistently so.],
)

All artifacts, per-generation metrics, quality ratings, seeds, and model snapshots are in the
public repository, with a one-command reproduction. Generations are content-cached, so a
re-run reproduces the same artifacts rather than merely the same statistics.

#bibliography("refs.bib", title: "References", style: "ieee")
