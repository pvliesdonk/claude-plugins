# persona-review

Review a document as its readers would, before they do. Simulated readers
walk it towards their own goals, editor lenses judge it against rubrics,
verifiers try to refute every finding against the text, and a synthesis
ranks what survives into an agenda for the author.

## Install

```
/plugin marketplace add pvliesdonk/claude-plugins
/plugin install persona-review
```

Then ask for it: "persona review of `docs/`", "review this paper as a
programme committee would", "red-team this proposal".

## Why it exists

The same review was built three times, from scratch each time: for a
product-security handbook (an SME CEO, a CTO, an engineer newly handed
security, procurement, production, a security expert, two readers outside the
target audience, plus style editors), for a scientific paper (scientists from
several fields, a programme-committee reviewer and an adversarial one), and
for a documentation site (an evaluator, a newcomer, a self-hoster, a power
user, a library consumer, an LLM client, an upgrader, a contributor). Each
run worked, and each rediscovered the same lessons:

- Readers who know the authors' intent cannot test whether the document
  conveys it. They get the back cover; the design notes go to the checkers.
- A reader's opinion is cheap; a reader walking towards a goal, with an entry
  point, a reading budget and a stop condition, finds what blocks people.
  Ending the walk with a teach-back that a verifier checks against the source
  catches the reader who finished confident and wrong.
- Reviewers recall facts wrongly and quote passages that do not exist. A
  verifier per reviewer, and a script that searches every quote, remove those
  before they reach the author.
- Several readers tripping on one deliberate design decision is evidence
  about the decision, and belongs in front of the author as a decision, not
  averaged away.

This plugin is those three runs, generalised and with their defects fixed.

## What it does

1. **Brief.** Finds the document's purpose, readers and reading seat, and
   sorts files into what readers get, what they must not see, and the ground
   truth verifiers check against.
2. **Ensemble.** Writes a card per reader: tier (primary, gatekeeper,
   secondary, adversarial), goal, entry point, stop condition, budget in
   words, and what they came for, written before reading. A distinctness test
   merges personas that would raise the same findings. You confirm the
   ensemble before anything runs. `presets.md` holds the three ensembles
   above and one for proposals.
3. **Run.** One reviewer per persona or lens, blind to the others; one
   verifier per reviewer that locates every quote, judges the teach-back and
   tries to refute the major findings; one synthesis. With the Workflow tool
   it runs as `workflows/persona-review.workflow.js`; without it,
   `scripts/run_offline.mjs` runs the same file with Agent-tool answers, so
   both paths share every prompt and filter.
4. **Report.** `scripts/render_report.py` writes the summary, ranked
   priorities, decisions for the author, a table of walks (goal reached,
   teach-back, words read against budget, reader state along the path), and
   per-reader detail. It searches every quote in the document itself, and
   compares against a previous round when given one.

## What it will not claim

Simulated readers predict reader problems; they do not observe them. Experts
asked to predict what real readers struggle with catch a minority of it, and
reviewers that are one model in several briefs agree more than independent
people would, and are kinder to text than readers are. The report says this,
lists the predictions that drive a priority with a cheap real-reader test for
each, and never reports reviewer satisfaction as a result. `evidence.md`
beside the skill gives the studies.

## Layout

```
persona-review/
├── skills/persona-review/
│   ├── SKILL.md            # the procedure
│   ├── ensemble.md         # every ensemble field, card-writing rules, example
│   ├── presets.md          # starting ensembles by genre
│   ├── evidence.md         # the studies behind the rules
│   ├── scripts/
│   │   ├── run_offline.mjs     # runs the workflow without the Workflow tool
│   │   └── render_report.py    # report, quote check, budgets, round comparison
│   └── tests/              # mechanics test (no model needed), pressure scenarios
└── workflows/persona-review.workflow.js   # prompts, schemas, verification, synthesis
```

## Cost

Two agents per reviewer and one synthesis: six personas and two lenses is
seventeen agents, most of them reading the whole document. The handbook
harness this replaces ran eight readers and a synthesis, without verifiers,
in about twenty minutes.

## Licence

MIT; see the [repository LICENSE](../../LICENSE).
