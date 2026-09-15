# Encoding Choice

A graphic is not chosen whole. It is **assembled from one decision per variable**, and each decision
can be judged on its own. Two frameworks do the work: Bertin's levels say what a channel *can* carry,
Mackinlay's criteria say in what order to apply the test.

## The move
- **Enumerate the variables first.** One line per thing the reader must get out of the picture. The
  chart type falls out of the assignment; it must not precede it.
- **Ask what level each variable's task needs**, then check the channel reaches it (Bertin, theory —
  a theorist's taxonomy, never experimentally validated, but it surfaces the right question):
  - *Selective* (isolate one category at a glance): size, value, hue, texture — **not shape**
  - *Associative* (see marks as one family while it varies): hue, texture, orientation, shape — **not size or value**
  - *Ordered* (read the steps as a sequence): position, size, value, texture — **not hue, shape, orientation**
  - *Quantitative* (read a ratio): **position and size only**
- **Spend the plane deliberately.** The two planar dimensions are the only channels carrying two
  variables at full strength. On a map or a network the plane is already spent on geography or
  topology, so accept that nothing left can be read quantitatively.
- **Match dominance to importance.** Size and value shout — they are selective *because* they
  dominate, and fail associative for the same reason. If a minor variable is in lightness, it will
  visually outrank the one carrying the argument.

## Apply it — expressiveness first, then effectiveness
**Expressiveness is a hard filter and binary** (Mackinlay; definitional, true by construction): the
encoding must state **all** the facts and **only** the facts. Read the encoding back as English
sentences — "twice the area means twice the value", "adjacent on this axis means adjacent in the
data", "this palette's midpoint is meaningful" — and any false sentence is a violation. A design that
fails is out of the running; no readability argument rescues it. The "only the facts" half is the one
that fails silently, because the surplus assertion was never consciously made.

**Then effectiveness, as a preference among survivors.** Its rankings differ by data type: "position
beats everything" is the *quantitative* ranking only; hue ranks second for nominal data and last for
quantitative. Mackinlay's ordinal and nominal rankings were never tested — say so if you stand on them.

**Cleveland & McGill is a tie-breaker for precise-value tasks, not a chart league table.** Position >
length > angle > area > volume > colour is real, replicated for the top five (Heer & Bostock), and
the bottom half is untested extrapolation. It measures *one* task — ratio estimation of two marked
values — and Saket et al. showed experimentally that **no chart wins across tasks** (bars for
clustering, lines for correlation, scatterplots for anomalies). Use it when the reader must estimate
*how much*; ignore it when the task is "is it going up" or "where is the outlier".

## Failure modes
- **Nominal on a continuous axis** — category codes on x assert an order and a spacing that do not exist.
- **The interpolating line** — connecting across a cohort change or a collection gap asserts a path you do not have.
- **Ratio by area on categories** — area reaches quantitative, so readers extract magnitude whether you meant it or not.
- **The associative violation** — the eye obeys the encoding, not the caption.
- **Categorical palette on ordered data** — hue has no order, so readers invent one, usually wrong.
- **The chart-type league table** — optimising the channel of a variable nobody reads precisely, while the argument's variable gets a weak one.

## Depth
`representing-information/perception-and-encoding/visual-variables-and-levels.md`,
`expressiveness-before-effectiveness.md` and `encoding-accuracy-and-its-limits.md` in an optional
source corpus (when available). For the folklore that descends from misreading these, see
`tool-contested-rules.md`.
