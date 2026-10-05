# persona-review

Review a document as its readers would, before they do. Each simulated
reader gets only what a real reader has and reads towards their own purpose;
editors check it against a rubric; a verifier per reviewer locates every
quote and tries to refute the major claims; a synthesis ranks what survives
into an agenda for the author.

## Install

```
/plugin marketplace add pvliesdonk/claude-plugins
/plugin install persona-review
```

Then ask for it: "persona review of `docs/`", "review chapter 3 as my
supervisor and an examiner would", "red-team this proposal". Before anything
runs, it shows you the readers it picked and the agent count, and waits for
your go-ahead unless you said to run without asking. A quick question about
one perspective ("how would a CISO read this paragraph?") gets a direct
answer, not a review.

Needs Python 3. With the Workflow tool the review runs as a workflow;
without it, `scripts/run_offline.mjs` (Node.js 18 or later) executes the
same workflow file with ordinary subagents, so both paths share every
prompt and check.

## What it adds to "review this as a CISO would"

A one-line persona prompt gets you one model's opinion in a costume. This
plugin changes what that model is allowed to know, what it must produce, and
what happens to its output:

- **Readers do not know what the authors meant.** Personas get the back
  cover, the reading seat and the reader-facing files. Design decisions,
  intended takeaways and source material go only to the verifiers and the
  synthesis, so a reader who misses the point is evidence, not a reviewer
  being polite about it.
- **Each reader has a reason to read.** A persona either *walks* (a goal, an
  entry point, a stop condition, a word budget, and a teach-back of what it
  came away with, which a verifier checks against the source) or *reads* (as
  the person would, saying where they would stop and why). You pick per
  persona; `ensemble.md` says which fits what.
- **Every finding quotes the document, and someone tries to knock it down.**
  A verifier per reviewer locates every quote, tries to refute up to ten
  major claims, judges the teach-back, and names up to three problems the
  reviewer missed. A script then searches every quote again by string match.
  Refuted and unlocatable findings are dropped, and listed so a wrong drop
  can be caught.
- **Disagreement goes to you, not to a vote.** Readers who want opposite
  things, or trip on a deliberate design decision, become decisions for the
  author with what evidence would settle each.

## What you get

One markdown file, `persona-review/<date>/report.md`, beside the document:

- a summary and ranked priorities, each with who raised it and where;
- decisions only the author can make;
- a table of readers: teach-back verdict, goal reached, words read against
  budget, reader state along the path, blockers / majors / minors;
- the predictions worth testing on one or two real readers, with how;
- per-reader detail with every finding's quote and verification;
- dropped findings, and a method section with the counts and caveats.

`skills/persona-review/tests/mechanics/` renders a small example from canned
answers: run `python3 tests/mechanics/test_mechanics.py` from the skill
directory.

## Cost

Two agents per reviewer and one synthesis; most of them read the whole
document. Measured on this plugin's own docs (about 5,200 words) with three
personas and one editor: 9 agents, about 840,000 tokens, about 10 minutes of
agent time with each stage run in parallel. Tokens grow with the document's
length times the number of reviewers. Levers, all in `ensemble.json`: fewer
personas, `coverage: path` so walkers stop at their budget, a cheaper
`model` or `verify_model`, and a lower `max_verify_per_reviewer`.

## What it will not claim

Simulated readers predict reader problems; they do not observe them. Human
experts asked to predict what real readers struggle with caught under 15% of
it. The reviewers are one model in several briefs, so they agree more than
independent people would, and models are kinder to text than readers are.
The checks above remove false findings; only the verifiers' search for
missed problems looks for false negatives, and it is the same model again.
So the report frames reader findings as hypotheses, never reports reviewer
satisfaction as a result, and labels goal reached and reading paths as the
simulated reader's own account. `evidence.md` gives the studies and what
they leave open.

No run has yet been scored against real readers. Record real-reader tests in
`reader_tests` and later rounds will weigh predictions by how they fared.

## Where it comes from

The same review was built by hand three times:

- a product-security handbook for small manufacturers: eight reader personas
  and two editors, run twice, the second round after the first round's fixes;
- a scientific paper: scientists from several fields, a programme-committee
  reviewer and an adversarial one (briefs not preserved);
- a documentation site of about 63,000 words: eight walking personas, run
  twice; blockers fell from 21 to 11 between rounds, and checking teach-backs
  against the code found examples that fail as written and a "read-only"
  setup that ran read-write.

This plugin generalises them, and fixes what their reports got wrong:
findings rendered without their quotes or verdicts, two personas whose
headings collided, hardcoded counts, refuted findings filtered only by a
prompt, and caps that truncated silently. `presets.md` holds their ensembles,
each marked with how much running it has behind it.

## Layout

```
persona-review/
├── skills/persona-review/
│   ├── SKILL.md            # the procedure
│   ├── ensemble.md         # fields, walk or read, card-writing rules
│   ├── presets.md          # starting ensembles by genre
│   ├── evidence.md         # the studies behind the rules
│   ├── scripts/
│   │   ├── run_offline.mjs     # runs the workflow without the Workflow tool
│   │   └── render_report.py    # report, quote check, budgets, round comparison
│   └── tests/
└── workflows/persona-review.workflow.js   # prompts, schemas, verification, synthesis
```

## Licence

MIT; see the [repository LICENSE](../../LICENSE).
