# Colour and Access

Colour is the channel people reach for first and reason about least, and the one where a design that
works for the author silently fails for a fraction of the audience. Both halves of this file are
about the same thing: what a reader can actually decode, given their vision, their medium and their
lighting.

## The move — colour
- **Pick the family from the data's structure, not from taste.** Unordered categories → qualitative
  (varying hue, roughly constant lightness). Ordered magnitude → sequential (a monotonic lightness
  ramp). Ordered around a *meaningful* midpoint → diverging. A diverging palette on data with no real
  midpoint invents a good/bad story the data does not tell.
- **Cap categorical hues at about seven.** Experimental work found three and five colours easy, seven
  and nine significantly harder. Beyond that, group, facet or direct-label — the number is a sound
  convention even though the Miller justification usually attached to it is not (`tool-contested-rules.md`).
- **Size the colour difference to the mark.** Discriminability depends strongly on mark type and
  size: thin lines and small scatter points need much larger colour differences than bars. A palette
  that tests fine on a bar chart can collapse on the scatterplot beside it.
- **Prefer a perceptually uniform ramp for continuous data**, and prefer a palette *designed* for
  colour vision deficiency over one retrofitted — the difference is that a designed one varies in
  lightness too, which is what makes it survive greyscale.
- **Never carry meaning in hue alone.** Encode redundantly: position, shape, direct labels, or
  ordering. This is also the first accessibility requirement, not a separate concern.

## The move — access
- **Red–green colour vision deficiency affects roughly 8% of men** and about 0.5% of women of
  northern European descent. This is not an edge case; in most rooms it is someone.
- **Luminance contrast and hue discriminability are independent.** Passing a text-contrast ratio says
  nothing about whether two series are distinguishable to a deuteranope. Check both, in a simulator.
- **Write alt text that states the finding**, then the chart type and range — not the construction.
  Blind readers rate the statistical and trend levels most useful, and typical alt text stops at
  "a bar chart of sales by region", which conveys almost nothing. Treat a generated description as a
  draft for a human to check: a reader cannot verify an interpretation they cannot see.
- **Accessibility is occasion-specific** (`tool-recutting.md`). Projectors crush darks and shift
  blues; board packs get photocopied into greyscale; a poster is read at two metres; a dashboard's
  red/amber/green status is the single most common failure, and needs an icon, a position or a word
  alongside the colour.

## Apply it
- Name the data's structure out loud before opening a palette — unordered, ordered, or ordered around
  a midpoint.
- Check the artefact three ways: in greyscale, in a CVD simulator, and at the size the marks will
  actually be.
- Ask what survives if colour is removed entirely. If the answer is "nothing", the encoding is not
  finished.
- Write the alt text as the claim sentence you already wrote for the title
  (`tool-titles-and-annotation.md`); if you cannot, the chart may not have a finding yet.

## Failure modes
- **Diverging on a fabricated midpoint** — a red-to-blue ramp that invents a neutral point and reads
  as good versus bad.
- **The legend nobody can map back** — twelve categories, twelve swatches, no direct labels.
- **Passing contrast, failing discriminability** — a palette signed off on a text-contrast rule while
  two of its series are the same colour to a tenth of the audience.
- **Status by hue alone** — red/amber/green tiles with no icon, position or word.
- **The palette that shrinks** — validated on bars, deployed on a scatterplot, where the differences
  vanish.
- **Construction alt text** — describing the picture instead of stating what it shows.

## Depth
`representing-information/perception-and-encoding/colour-decisions.md` and
`representing-information/audience-and-literacy/accessibility-across-media.md` in an optional source
corpus (when available).
