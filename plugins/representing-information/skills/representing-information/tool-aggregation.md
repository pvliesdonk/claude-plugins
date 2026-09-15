# Aggregation and Load

Two things masquerade as rendering decisions and are not. **Aggregating** is a statistical claim
about the unit of analysis; **"reduce cognitive load"** is an unactionable slogan unless you name
which load. Both bite hardest when someone has decided a display "has too much in it".

## The move — aggregation is a claim
- **Name the unit of analysis in one sentence, and put it on the display.** "One dot is one order."
  "One bar is one branch-quarter." An unstated unit is where the ecological fallacy enters.
- **Check whether group weights move across the comparison.** An aggregate is a weighted average
  with two inputs; if the weights shift, it can move *against every component* — Simpson's paradox
  formally, a composition shift in everyday reporting, and it affects any weighted sum or average
  (mathematical fact, not opinion). If weights move, show them or decompose; never let a single
  aggregate line be the only view.
- **Respect the ecological fallacy** (Robinson, a statistical result): group-level relationships
  need not hold at individual level. A regional chart does not describe people.
- **Label the bin, and test the zoning.** The **modifiable areal unit problem** has two components:
  *scale* (county vs tract vs block changes the correlations) and *zoning* (the same-sized units
  redrawn relocate the hotspots). Bin geometry is a free parameter you chose, so a histogram's
  shape and a map's hotspots are partly artefacts. Re-bin at a different width; if the story does
  not survive, the story was about the bins.
- **Treat "Other" as a claim** that its contents are individually immaterial — not a tidy-up.

## The overplotting ladder
Each rung gives something up; climb only as far as you must, and say which rung you are on.
**Alpha blending** (keeps every point, saturates) → **jitter** (small positional lies) →
**sampling** (keeps the shape, *loses outliers* — fine for private structure-checking, disqualified
when outliers are the point) → **binned aggregation** (preserves the marginal distribution, costs
individual identity) → **density/contour** (costs the marks; the reader is looking at an estimate).

## Apply it — load
- **Only extraneous load is yours to cut.** Intrinsic load is fixed by changing the level of
  abstraction, not the display; germane load is learning, and cutting it leaves something easy to
  look at and impossible to learn from.
- **A legend is a split-attention machine** — two sources, each useless alone, separated by a
  saccade. So is a caption defining a mark, a footnote defining a series, and a tooltip carrying
  information the static view needs. **Direct labelling is the canonical fix**: name on the line,
  value beside the mark, unit in the axis title. Treat a legend as a failure to be justified — above
  roughly six series (convention), or where series are genuinely unnameable in the plot area.
- **Test redundancy by register.** Same claim in a *different* register (a title stating what the
  chart shows) aids recall; the same values in the *same* register (a table beside its own bar
  chart) is a reconciliation task and nothing else.
- **Cowan's ~4 governs items held across views, never marks within one.** Budget it for series
  tracked mentally, filter states, panels consulted together, and values remembered from a previous
  slide. A five-thousand-point scatterplot imposes almost no working-memory load for "is there a
  trend". Quoting 7±2 to cap marks, bars or categories is the commonest abuse of psychology here;
  see `tool-contested-rules.md`.

## Failure modes
- **Aggregating to hit a density target** — a presentation decision silently making a statistical one.
- **The "aggregate looks fine" report** — every component deteriorating, the headline flat, because the mix moved.
- **Bin size chosen for smoothness** — MAUP operating as an authoring convenience.
- **The lying "Other"** — a long tail swept into one bucket, often justified by a misapplied 7±2.
- **Sampling away the outliers** in a display whose purpose is to find them.
- **"Reduce cognitive load" as a review comment** — name the source: split attention, within-channel redundancy, or cross-view carry.

## Depth
`representing-information/density-and-reduction/aggregation-as-a-claim.md` and
`cognitive-load-and-working-memory.md` in an optional source corpus (when available). Caveat: the
split-attention and redundancy effects were established on instructional text-and-diagram materials;
their transfer to charts is a structural inference, not a tested result.
