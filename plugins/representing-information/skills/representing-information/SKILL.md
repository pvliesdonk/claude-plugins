---
name: representing-information
description: Use when deciding WHAT to show, HOW MUCH of it, and IN WHAT FORM for a particular audience — the judgment behind a visualisation rather than the drawing of one. Covers choosing a representation for measurements, an ontology or taxonomy, a process or causal claim, or qualitative findings; taking one analysis to executives, technical peers, the public, a workshop, a dashboard, a talk, a poster or a paper; deciding how much detail an audience can actually take; working out whether a picture is warranted at all (often it is not); and telling honest emphasis from quiet persuasion. Use this whenever someone asks how best to present, communicate or explain data or a model to an audience, what belongs on a slide or in a board pack, how much to simplify, how to show uncertainty, or whether a chart is misleading — even if they do not say the word "visualisation". This is the judgment layer: for rendering charts use the dataviz skill, for diagram syntax use creating-diagrams.
---

# Representing Information

Distilled craft for deciding what a picture should contain, for whom, and whether it should exist.
Each occasion and each kind of material has its own reference file with a recipe — what to show, how
much, what to cut, and how it fails. **Identify the occasion, load its file, follow it.** Don't
design from the router alone.

This skill stops at the decision. Rendering belongs elsewhere: `dataviz` for chart construction,
`creating-diagrams` for diagram syntax and layout.

## Route to the occasion

An occasion is not a file format. It is a combination of four variables — **dwell time**, **author
presence**, **the reader's next action**, and **control of the view** — and those four, not the
chart type, decide what belongs in the picture.

| The artefact is for… | Load |
|---|---|
| A live talk, a conference slide, anything narrated while shown | `live-talk.md` |
| An executive briefing, board pack, or decision memo | `executive-briefing.md` |
| A report, paper, or any figure that must stand alone in a document | `report-figure.md` |
| A monitoring dashboard — a surface checked repeatedly, no question asked | `monitoring-dashboard.md` |
| A public explainer, article, or anything a reader may simply abandon | `public-explainer.md` |
| A workshop or co-design session, where people mark it up | `workshop-artefact.md` |
| A poster or large-format print read at a distance | `poster.md` |
| Yourself, exploring — no audience yet | `own-exploration.md` |

## Route by material

Reach for these *in addition* to the occasion file when the material is not simply magnitudes. They
decide what the picture can contain; the occasion file decides how much of it survives.

| The material is… | Load |
|---|---|
| An ontology, taxonomy, knowledge graph, schema or domain model | `domain-models.md` |
| A process, flow, mechanism, or a causal claim | `processes-and-causality.md` |
| Interviews, themes, free text, documents — material that resists counting | `qualitative-material.md` |

**No exact match, unsure, or suspicious that no picture is needed?** Load `choosing.md`. It runs the
prior question — whether to draw at all — then diagnoses the job and shows how to assemble the right
tools. The core moves below hold everywhere.

## Core moves (every representation)

Apply these before any occasion-specific step. Capable practitioners — humans and models — reliably
do **1** well and skip **2–6**. Check each explicitly:

1. **Encode competently.** Position for quantities, a colour family matched to the data's structure,
   direct labels over legends, nothing decoded by area or volume that matters precisely. This is the
   part that usually goes right, and it is the least of the job.
2. **Name the operation before the form — and check a picture is warranted.** State what the reader
   must *do* in vocabulary containing no chart name ("compare five regions, find the anomalous
   one"). This is where the costly failures originate, and no polish downstream repairs them. Then
   ask whether a sentence, a number or a table would serve better. Frequently it would: tables win
   for lookup, exact values and threshold checks, and many requests to "visualise this" resolve to
   one sentence.
3. **Score the occasion, then cut to it.** Dwell time, author presence, next action, control of the
   view. Density is not a property of a display — it is a property of a display plus a reading
   contract. What an analyst reads at leisure and what a board reads in forty seconds are different
   artefacts, not different sizes of one.
4. **Put the claim in the title, as a sentence.** "Renewals fell a fifth after the price change",
   never "Renewals by quarter". The title is the highest-leverage and least-reviewed channel in the
   artefact: readers' recall matches the title more often than the chart, and a slanted headline
   still reads as impartial. If you cannot write the sentence, you do not yet have a finding.
5. **Show uncertainty as a range, never as a hedge.** Numeric uncertainty costs almost no trust;
   vague verbal hedging ("indicative only", "treat with caution") costs more and conveys nothing.
   Bare bar-plus-error-bar is a poor default. And when the honest answer is that nothing can be
   distinguished, say *that* in the title.
6. **Re-cut for a new audience; don't resize — and be willing to start from scratch.** The claim,
   the data, the uncertainty, the denominator and the effect's direction and magnitude stay fixed.
   Everything else is free. Deriving a variant from a finished artefact anchors you to its buried
   decisions, so starting again from the material is often the better answer and a legitimate
   recommendation. Adapting the *form* is adaptation; changing the comparison, baseline, window or
   denominator by audience is persuasion.

Then open the occasion file and follow its recipe.

## Underlying techniques (tools)

The core moves and occasion recipes draw on cross-cutting tools — task abstraction, encoding choice
and the field's contested rules, density and reduction, audience literacy, uncertainty, titles and
annotation, re-cutting across audiences, the honesty line, colour and accessibility, structured
critique, and the decision not to draw. When designing or (especially) reviewing and you want the
technique itself, see `tools.md` for the index and the matching `tool-*.md` file.

## Neighbouring skills

This skill is the picture-side counterpart to two others, and defers to them rather than repeating
them:

- **`writing-nonfiction`** — a figure inside a document is part of that document's argument. That
  skill decides the genre, the spine and the reader; this one decides what the figure carries and
  whether it should exist. When a document is the deliverable, start there and come here for the
  figures.
- **`hosting-workshops`** — an artefact made for a session is an instrument of the session design.
  That skill decides whether to convene and what the session must produce; this one decides what to
  put in front of the room. `workshop-artefact.md` is the seam.
- **`dataviz`** and **`creating-diagrams`** own rendering — chart construction, diagram syntax,
  layout. Decide here, draw there.

## A warning about this field's folklore

More than neighbouring crafts, visualisation circulates confident rules whose evidence does not
support them. Pie charts are not read by angle. "Always start at zero" is the wrong formulation of a
real problem. "One idea per slide" has never been tested. Overview-first is thinly evidenced.
Squarified treemaps are not perceptually optimal. These files mark what is experimental, what is
convention, and what is contested — don't flatten that, and don't defend a folklore rule to an
expert audience.

## Depth

These files distill the **Representing Information** corpus. Each file names an optional source note
for more depth when a connected knowledge base provides it, but the skill never depends on that
source.
