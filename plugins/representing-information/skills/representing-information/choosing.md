# Choosing — Should There Be a Picture, and Which One?

Most bad representations were the wrong artefact, chosen before anyone asked what job it had to do.
This file runs the prior question, then diagnoses the job and shows how to assemble the tools.

## First: should this be a picture at all?

A drawing is not the default. Cognitive fit theory is the one real theory here and it is unambiguous:
**tables are symbolic** and suit lookup, exact values and threshold checks; **graphs are spatial**
and suit patterns, trends and exceptions. A reader who needs the Q3 figure wants a number; a reader
who needs to know whether Q3 broke the trend wants a line.

Rule it out first:

- **One comparison the reader will act on** → a sentence. "Renewals fell a fifth after the price
  change" is faster to read and harder to misread than any chart of it.
- **Exact values, lookup, a threshold check** → a table. Tables are exact, checkable, impose no
  smoothing, and survive being pasted somewhere else.
- **Fewer than roughly two dozen cells** → a table, almost always.
- **The material can't support the question** → say so, and say what it *can* support. A picture
  doesn't repair a missing denominator; it hides one.

Draw when the reader must see a **shape**: a trend, a distribution, an outlier, a structure, or a
comparison across more items than they can hold in mind. Many requests to "visualise this" honestly
resolve to a sorted list or one sentence — delivering that is the professional answer, not a lesser
one. (`tool-when-not-to-draw.md`)

## Then: name the operation, not the form

State what the reader must *do*, in vocabulary containing no chart name.

> "Compare the distribution of settlement times across five regions and identify the anomalous one."

That is a task abstraction. "Make a box plot" is not. This is the highest-consequence step in the
whole skill: an error here cascades, and no quality of encoding downstream repairs a picture that
shows the wrong thing. If you can't state the operation without naming a chart, you have a
preference, not a design. (`tool-task-abstraction.md`)

Chart choosers (Abela's grid, the FT Visual Vocabulary) belong *after* this step. They're useful as
vocabulary — a real bottleneck — but their input is a data shape plus a vague verb, so they can't
tell you the question is wrong or that no chart is warranted. Use one to generate alternatives, not
to end the decision.

## Then: classify the job

Name the **dominant material** (even mixed material has one that leads):

| The material is… | Load |
|---|---|
| Magnitudes — counts, rates, money, time series | the occasion file + `tool-encoding-choice.md`, `tool-how-much.md` |
| Structure — ontology, taxonomy, graph, schema | `domain-models.md` |
| Process, mechanism, or a causal claim | `processes-and-causality.md` |
| Interviews, themes, free text, documents | `qualitative-material.md` |

An ontology with instance counts is structure first, magnitude second. Drawing it as a chart of
counts loses what made it an ontology; drawing every instance loses the counts in a hairball.

## Then: match the container to the occasion

Score the four variables — **dwell time**, **author presence**, **the reader's next action**,
**control of the view** — and load the matching occasion file. The same operation on the same
material, for a different occasion, is a different artefact.

- Narrated while shown, seconds of dwell → `live-talk.md`
- Someone decides from it, hostile scrutiny, author often absent → `executive-briefing.md`
- Re-readable, self-contained, no author → `report-figure.md`
- Checked repeatedly, no question asked → `monitoring-dashboard.md`
- Voluntary attention, abandonable → `public-explainer.md`
- People mark it up in the room → `workshop-artefact.md`
- Read at two metres then at half a metre → `poster.md`
- No audience yet → `own-exploration.md`

## Hybrids and no-match

Most real artefacts are hybrids — a board pack that will also be presented, a report figure destined
for a conference slide. Take the **dominant** occasion's recipe as the spine and graft in what the
secondary use needs, or better, make two artefacts. The common error is one artefact aimed at two
occasions, which reliably serves neither.

If the work already exists and the *audience* changed, don't start here — go to
`tool-recutting.md`. Its headline: re-cut rather than resize, and starting again from the material
is often the right answer rather than a failure.

## Failure modes

- **The defaulted chart** — drawing because a request mentioned data, when a sentence was the answer.
- **Form before question** — a chart type chosen first, the operation reverse-engineered to fit.
- **The tool's default as the decision** — the software offered something and that became the design.
- **The favourite form** — everything becomes a bar chart, a network diagram, or a dashboard.
- **Unnamed dominant material** — a mixed artefact with no centre of gravity, so nothing lands.
- **The compromise artefact** — one picture for two occasions, too dense for one and too thin for the other.

## Depth

`representing-information/typologies/choosing-a-representation.md` and
`representing-information/typologies/the-occasion-typology.md` in an optional source corpus (when
available).
