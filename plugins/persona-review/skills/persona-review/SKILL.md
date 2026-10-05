---
name: persona-review
description: Use when a whole written document should be reviewed by simulating the people who will read it, before they do: a report, paper, thesis chapter, white paper, handbook, proposal, policy, or software documentation site. Triggers on "persona review", "review this as its readers would", "red-team this proposal", "pre-submission review", or a second round after revisions. Picks the readers, writes a card for each, runs blind reader reviews and editor lenses as subagents, has a verifier locate every quote and try to refute the major claims, and writes a ranked report with the decisions only the author can make. For a quick single-perspective question ("how would a CISO read this paragraph?"), answer directly instead. Not for code review, and not for drafting.
---

# Persona Review

Terms used throughout: a **persona** is a simulated reader, a **lens** is a
simulated editor holding a rubric, a **reviewer** is either. The report is the
deliverable, and it predicts reader problems rather than observing them.

## Rules for the whole review

- Do not edit the document until the report exists. Every reviewer reads the
  version recorded as `pin`: a commit SHA, or the date and the `sha256sum` of
  the reader files when there is no git.
- Personas get only what a real reader has: `back_cover`, `seat` and
  `reader_files`. Design intent goes in `design_context`, takeaways in
  `intended_takeaways`, conventions and fact registers in `withheld` (and in
  `ground_truth` when verifiers need them).
- Keep the author's opinion of the document out of every card and brief.

## Step 1: Brief

1. Create the run directory: `persona-review/<date>/` beside the document;
   use the project's notes directory instead when the document's own
   directory is built or published.
2. If the document is not on disk (pasted text, a shared doc), save it there
   as markdown; reviewers and scripts read files.
3. Find what the document is for, what it should make a reader do, and when
   and where it will be read. Skim its structure; do not judge it.
4. Ask the author, in one message: who actually reads it, and any real reader
   evidence (support questions, earlier review comments); whether an AI model
   drafted it, because that changes how the report weighs reader
   satisfaction. Proceed on stated assumptions if they do not know.

## Step 2: Ensemble

Read `ensemble.md` for the fields and the walk-or-read choice, and
`presets.md` for starting ensembles.

1. Use one persona per distinct reader the document has: usually 3 to 6.
   When it has one real reader (a thesis chapter for a supervisor), use that
   reader and an adversarial one. Add a persona only if it has a different
   goal or reads a different part, and mark every persona the author did not
   name `inferred` or `assumed`.
2. Choose each persona's mode. **walk** (goal, entry point, stop condition,
   word budget, a teach-back the verifier checks) fits a document consulted
   to get something done. **read** (reading as the person would, saying where
   they would stop) fits a document read through, where the question is
   trust, persuasion or reception. One ensemble may mix them.
3. Write `came_for` from the reader's situation, before reading the document
   closely.
4. Test distinctness: for every pair of personas, name one finding one would
   raise and the other would not. If you cannot, merge them.
5. Cover the tiers the document has: a primary reader; the gatekeeper who
   decides acceptance, funding or purchase; an adversarial reader for a
   persuasive document; a reader arriving cold mid-document for anything
   consulted rather than read through.
6. Add 1 to 3 lenses. Use the project's style guide as a lens rubric when one
   exists; otherwise write the author's stated house rules into the lens
   brief. Add a significance lens for papers and proposals, and a compliance
   lens with the call text as rubric for proposals.
7. Show the user the ensemble as a table (key, tier, mode, goal, entry,
   budget, came_for, source) with the agent count: two per reviewer plus
   one. Wait for confirmation unless they said to run without asking.
8. Now collect what only verifiers and the synthesis see: ask the author for
   deliberate design decisions, what a reader must leave with, and what
   "done" means, and sort the remaining files into `withheld` and
   `ground_truth`. Doing this after the cards keeps it out of them.
9. Write `ensemble.json` to the run directory.

## Step 3: Run

`<skill>` below is the base directory shown when this skill loaded;
`<plugin>` is two levels above it.

**With the Workflow tool:**

    Workflow({ scriptPath: "<plugin>/workflows/persona-review.workflow.js",
               args: <the ensemble object> })

Pass `args` as the object, not a JSON string. Save the returned object to
`<run-dir>/result.json`. A result with `stage: "args"` lists what to fix in
`problems`.

**Without it, with the Agent tool:** the runner executes the same workflow
file, answering its agents from files.

    node <skill>/scripts/run_offline.mjs <run-dir>/ensemble.json <run-dir>

It stops three times with prompts pending: reviewers, then verifiers, then
the synthesis. At each stop, answer every pending prompt in one message, one
`general-purpose` Agent per prompt, each told: "Your brief is in <prompt
file>. Read it and follow it exactly." Then run the command again. Exit 0
means `<run-dir>/result.json` is written. On any other exit, show the user
the output and stop.

**Without subagents:** write each pending prompt's answer yourself, in order,
and pass `--runner in-context`. Tell the user first that the reviews will not
be blind; the report records it.

After any path, confirm the reader files still match `pin`. If a reviewer
changed one, name the files to the user and stop.

## Step 4: Render and check

    python3 <skill>/scripts/render_report.py <run-dir>/ensemble.json \
      <run-dir>/result.json -o <run-dir>/report.md --root <dir the reader_files paths are relative to>

Read *Method and caveats*. Check by hand against the document: every quote
the script could not find, one dropped finding, one finding the verifier
added, and the top priority's evidence. If a check fails, say so in the
hand-over; do not edit the reviewers' words.

## Step 5: Hand over

Give the user the summary, the top three priorities, the decisions only they
can make, and the report's path. Do not start fixing unless asked. Offer to
file each verified blocker as its own issue, with the writing-issues skill
when installed; ask before filing.

## Second and later rounds

1. Reuse the ensemble; change only `date`, `pin` and moved paths.
2. Add `previous`: its date, pin, priority titles, and in `rewritten` the
   sections changed since.
3. Add each real-reader test the author ran to `reader_tests` with its
   outcome (confirmed, refuted, untested), so the synthesis weighs
   predictions of the same kind by how they fared.
4. Render with `--previous <old run-dir>/result.json`.
5. In the hand-over, name everything that differs between rounds besides the
   document.

The studies behind these rules, and what they leave open, are in
`evidence.md`.
