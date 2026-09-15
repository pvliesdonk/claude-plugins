# How Much to Show

Density is not a property of a display. It is a property of a display **plus a reading contract** —
who reads it, how often, and who bears the cost of a misreading. The same material honestly supports
a twenty-panel grid and a single annotated line, and neither is the more rigorous choice.

## The move — name the contract first
> **Who is allowed to be wrong in front of this, and for how long?**

| Answer | Contract | What it licenses |
|---|---|---|
| Me, privately, for thirty seconds | **Exploratory** | Maximum density, no polish, many cheap displays |
| Nobody — an audience forms a belief in one pass | **Explanatory** | Aggressive reduction, one dominant message, annotation |
| The same trained reader, daily, who notices anything odd | **Monitoring** | High density, learned encodings, no narration |

The monitoring case rests on **amortisation**: the learning cost of a dense encoding is paid once
and spread over every later glance. Check the claim before invoking it — a surface read quarterly by
a rotating cast is an explanatory artefact in a monitoring costume. ("Dashboard" names a container,
not a contract; Sarikaya et al. found real dashboards span at least three incompatible jobs.)

## Apply it — reduction
**Data-ink is a diagnostic, not an objective.** Tufte is a maximalist about *data* and a minimalist
only about *ink per datum*; the popular "strip everything" version is neither his argument nor
supported. Ask "what is this element doing?" of every mark; never optimise the ratio, because the
cheapest way to raise it is to delete what the reader needs. Ajani et al. tested the two halves
separately (the best experimental support the programme has): **declutter buys professionalism
ratings; focus — a message-bearing headline, one highlighted subset, connected annotations — buys
clarity and memory for the highlighted pattern.** Erasure is preparation for emphasis, not the point.
If you have stripped a chart and highlighted nothing, you are half done. Pushback worth carrying:
embellishment aided *recall* (Bateman et al., with weak plain comparators and costs under time
pressure), and redundancy helps (Borkin 2016) — in tension with "erase redundant data-ink".

## Apply it — comparison and navigation
- **Three strategies** (Gleicher et al., a design-space taxonomy, not a ranking): **juxtapose** ·
  **superimpose** · **encode the difference**. The third is systematically under-used — if the
  finding is "A is 12% above B", plot A minus B rather than leaving the subtraction to the reader.
- **Superposition beats standard juxtaposition for pairs** (Ondov et al., experimental). Small
  multiples suit pattern-level comparison across many conditions — with consistent scales, a
  meaningful sort, and highlighting on the frames that matter.
- **Small-multiple accuracy declines linearly with frame count** (Hosseinpour et al.) — and *not*
  because frames shrink, so the mechanism is visual search. Highlighting the frames to compare was
  the measured mitigation. Past roughly nine to twelve frames (convention, not a threshold), sort,
  aggregate, or add a summary panel naming which frames differ.
- **Animation loses to small multiples for analysis, wins for presentation** (Robertson et al.).
- **Sequence for argument, multiples for comparison** — a slide transition dumps the prior view out
  of working memory, so never sequence where the point *is* a comparison.
- **Overview-first is thinly evidenced.** Shneiderman's mantra is theory; Craft & Cairns found it
  used as post-hoc cover, Hornbæk & Hertzum found no stable definition of "overview", and
  overview+detail was often *preferred* yet *slower*. Keep it when the reader does not know where to
  look; when they arrive with a target, search first and show context *around* the answer.

## Failure modes
- **Polishing during exploration** — the invisible failure; it costs insights and leaves no artefact to inspect.
- **Shipping the notebook** — exploratory density delivered to a one-pass audience, defended as "showing all the data".
- **The Tufte-compliant mute** — spare, clean, no claim, no direct labels, communicating nothing.
- **Deleting data to raise the ratio** — that is aggregation without a stated claim; see `tool-aggregation.md`.
- **The forty-panel wall** — a search problem handed to the audience; free scales and alphabetical order make it worse.
- **The KPI parade** — six unowned tiles occupying the prime space above the charts people actually open the page for.

## Depth
`representing-information/density-and-reduction/exploratory-explanatory-and-monitoring.md`,
`reduction-and-the-data-ink-programme.md`, `comparison-layouts.md` and
`overview-detail-and-progressive-disclosure.md` in an optional source corpus (when available).
