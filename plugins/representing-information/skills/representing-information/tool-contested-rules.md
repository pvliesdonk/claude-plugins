# Contested Rules

A ledger of the rules this field circulates more confidently than its evidence warrants. Use it
before asserting a rule, and when one is asserted at you. The point is not contrarianism: several
entries are broadly right and only their stated *mechanism* is wrong; one is right in its domain and
overextended; one is refuted.

## The ledger

**Pie charts.** *As circulated:* bad, because humans judge angles poorly. *Research:* the mechanism
does not exist. Skau & Kosara found **angle is the least important cue**; **area** fits estimates
best, arc length close behind — and donuts, which have no centre angle, are as accurate. Spence &
Lewandowsky found pies equal to bars for simple proportions and **better** for composite comparisons
(A+B vs C+D); Heer & Bostock found angle not worse than length. *Verdict:* the confident rule is
folklore, a narrower one survives — poor for ranking many categories, small differences and time
series; legitimate for part-to-whole at roughly five to seven slices.

**3D.** *As circulated:* depth effects destroy accuracy. *Research:* Zacks et al. found 3D
perspective did lower accuracy — but the effect **vanished with a short delay**, while
**neighbouring-element effects were about an order of magnitude larger** and survived. *Verdict:*
gratuitous 3D is still a bad idea, for reasons the rhetoric omits — occlusion, ambiguous baselines,
foreshortening. The better-evidenced and almost undiscussed problem is what sits *next to* a mark.

**Dual axes.** *As circulated:* never; they manufacture spurious correlations. *Research:* one study
(Isenberg et al., on dual-*scale* charts) found superimposed designs worst on accuracy and time —
thin. The stronger objection is **semantic, not perceptual**: the crossing point means nothing and
either axis can be slid to manufacture a story, a free parameter the reader cannot see. *Verdict:*
the warning is sound, the empirical base thinner than its confidence. Prefer indexing to a common
base, small multiples or a connected scatterplot; if unavoidable, use two units of the *same*
quantity.

**Rainbow colourmaps.** *As circulated:* always wrong. *Research:* genuinely contested, with
experimental evidence on both sides. Liu & Heer found rainbow degrades magnitude ordering but carries
**no penalty for reading local detail**; Gołębiowska & Çöltekin confirmed the ordering deficit
(37,000+ figures, 544 participants); Ware, Stone & Szafir argue the hue segmentation that harms
ordering **helps value look-up and feature detection**. *Verdict:* bad for ordered-magnitude
comparison and for colour vision deficiency; defensible for point look-up and fine structure, which
is what many scientific users are doing. Not a default, not automatic malpractice either.

**Squarified treemaps.** *As circulated:* squares are easiest to judge. *Research:* **refuted.** Heer
& Bostock found aspect ratio **1:1 was the worst**, robustly, in both plain-rectangle and treemap
conditions — people use side length as a proxy for area, and a square is where that proxy maximises
error. *Verdict:* squarification may still win on stability under updates and label legibility. Those
are legitimate arguments; perceptual accuracy is the opposite of the result.

**"7±2".** *As circulated:* limit categories, legend entries or tiles to seven, because that is
working-memory capacity. *Research:* right number, wrong reason. Miller's result is about
**sequentially presented** items held in memory; a legend is simultaneously visible and re-readable.
Healey separately found three and five colours easy, seven and nine significantly harder — a
discriminability finding about *colour*, not about counting anything. *Verdict:* keep the number as a
convention for categorical colour; drop the Miller justification, which collapses when checked.

## Apply it
- **Before asserting a rule**, state the narrower version you can actually defend.
- **When a rule is asserted at you**, offer the narrower form both parties can agree on. Most of
  these arguments are winnable in one sentence.
- **Recognise the pattern in rules not yet listed:** a real, narrow finding acquires a mechanism it
  never had, and the mechanism licenses generalisations the finding never supported.

## Failure modes
- **Defending folklore to an expert** — the fastest way to lose a design review you were right about.
- **Contrarian over-correction** — "pies are fine, actually" is as wrong as the rule it replaces.
- **Laundering theory into evidence** — citing an untested taxonomy cell or ranking half as a finding.
- **Arguing encoding rules when the abstraction is wrong** — all of these are level-3; see `tool-task-abstraction.md`.

## Depth
`representing-information/perception-and-encoding/contested-rules.md` in an optional source corpus
(when available). Caveat carried from it: most of this literature is crowdsourced ratio estimation
with non-expert participants, effect sizes are rarely reported usefully, and replication is sparse —
several entries are unresolved rather than settled in either direction.
