---
name: persona-review
description: Use when a written document should be reviewed by simulating the people who will read it, before they do: a report, paper, white paper, handbook, proposal, policy, or software documentation site. Triggers on "persona review", "review this as the readers would", "how would a CISO / programme committee / newcomer read this", "red-team this proposal", "pre-submission review", or a second round after revisions. Picks the readers, writes a card per reader with a goal, entry point, reading budget and expectations, runs blind reader walks and editor lenses, verifies every finding against the text, and writes a ranked report with the decisions only the author can make. Not for code review, and not for drafting.
---

# Persona Review

Simulated readers walk the document towards their own goals; editor lenses
judge it against rubrics; verifiers try to refute what they report; a
synthesis ranks what survives. The review is the deliverable. It predicts
reader problems; it does not observe them, and the report says so.

## Rules for the whole review

- Do not edit the document during the review. Every reviewer reads the same
  version, recorded as `pin` (a commit SHA, or the date and a file hash).
- Give readers only what a real reader has: the back cover, the reading seat
  and the reader-facing files. Design intent, conventions, fact registers and
  intended takeaways go in the fields only verifiers and the synthesis see.
- Keep the author's opinion of the document out of every prompt. "I think
  it's strong" in a brief tilts every reviewer towards agreeing.
- Present reader-experience findings as predictions to test, never as what
  readers think.

## Step 1: Brief

1. Find the document's files, its purpose, who it is for, what it should
   make a reader do, and when and where it will be read. Skim its structure;
   do not judge it yet.
2. If the document is not on disk (pasted text, a shared doc), save it as
   markdown in the run directory first; the scripts and reviewers read files.
3. Ask the author, in one message, for what you cannot infer: who actually
   reads it (and any real reader evidence: support questions, earlier review
   comments), what a reader must leave with, which features are deliberate
   design decisions, what "done" means, and whether an AI model drafted it.
   Proceed on stated assumptions if they do not know.
4. Sort the files into `reader_files` (what a reader gets), `withheld`
   (authors' internals) and `ground_truth` (what the document describes:
   code, a fact register, cited sources).

## Step 2: Ensemble

Read `ensemble.md` for the card fields and `presets.md` for starting
ensembles. Then:

1. Pick 3 to 6 reader personas and 1 or 2 editor lenses. Add more only when
   each extra reader has a different goal or reads a different part.
2. Write each card from the reader's situation, not from what the document
   contains: `came_for` is what this reader expects before opening it.
3. Give every persona a goal, an entry point, a stop condition reachable by
   reading, and a budget in words.
4. Test distinctness: for every pair of personas, name one finding one would
   raise and the other would not. If you cannot, merge them.
5. Cover the tiers the document has: at least one primary reader; the
   gatekeeper who decides acceptance, funding or purchase; an adversarial
   reader for a persuasive document; a reader who arrives cold mid-document
   for anything consulted rather than read through.
6. Prefer the project's own style guide as a lens rubric; otherwise use an
   installed style skill (govuk-style, writing-nonfiction's `tool-*.md`). Add
   a significance lens for papers and proposals.
7. Show the user the ensemble as a table (key, tier, goal, entry, budget,
   came_for, source) with the agent count: two per reviewer plus one. Wait
   for confirmation unless they said to run without asking.
8. Write `ensemble.json` to the run directory: `persona-review/<date>/`
   beside the document, or the project's notes directory. Never inside a
   directory the project builds or publishes.

## Step 3: Run

Paths below are relative to `${CLAUDE_PLUGIN_ROOT}`; outside a plugin
install, `workflows/` is two levels above this file and `scripts/` is beside
it.

**With the Workflow tool:**

    Workflow({ scriptPath: "${CLAUDE_PLUGIN_ROOT}/workflows/persona-review.workflow.js",
               args: <the ensemble object> })

Pass `args` as the object, not a JSON string. When it completes, save the
returned object to `<run-dir>/result.json`, or copy the task output file
the completion notice names; the renderer accepts that wrapper too. A result with `status: "error"` and
`stage: "args"` lists what to fix in `problems`.

**Without it, with the Agent tool:**

    node ${CLAUDE_PLUGIN_ROOT}/skills/persona-review/scripts/run_offline.mjs <run-dir>/ensemble.json <run-dir>

Exit 3 lists pending prompts. Answer all of them in one message, one
`general-purpose` Agent per prompt, each told: "Your brief is in <prompt
file>. Read it and follow it exactly." Run the command again; repeat until
it exits 0. One message per pass keeps the reviewers blind to one another.

**Without subagents:** answer each pending prompt yourself, in order, and
pass `--runner in-context`. Tell the user first that the reviews will not be
blind; the report records it.

After any path, confirm no reviewer changed a reader file (`git status
--porcelain`, or the hash in `pin`). If one did, stop and name the files to
the user before rendering.

## Step 4: Render and check

    python3 ${CLAUDE_PLUGIN_ROOT}/skills/persona-review/scripts/render_report.py \
      <run-dir>/ensemble.json <run-dir>/result.json -o <run-dir>/report.md --root <project root>

Then read the report's *Method and caveats* section and check by hand
against the document: every quote the script could not find, one dropped
finding, and the top priority's evidence. Correct the report's framing if a
check fails; do not edit the reviewers' words.

## Step 5: Hand over

Give the user the summary, the top three priorities, the decisions only they
can make, and the report's path. Do not start fixing unless asked. Offer to
file each verified blocker as its own issue (with the writing-issues skill
when installed); majors and minors stay in the report. Filing is outward-
facing: ask first.

## Second and later rounds

Reuse the ensemble unchanged except `date`, `pin` and any moved paths, and
add `previous` (date, pin, the previous priorities' titles). Render with
`--previous <old run-dir>/result.json`. In the hand-over, name everything
that differs between rounds besides the document, so the comparison can be
weighed.

## Reference

- `ensemble.md`: every ensemble field, budgets, card-writing rules, example.
- `presets.md`: ensembles for handbooks, papers, software docs, proposals.
- `evidence.md`: the studies behind the rules above, and what they do not
  settle.
- `tests/`: a mechanics test that runs without a model, and pressure
  scenarios.
