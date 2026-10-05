# Tests for `persona-review`

## Mechanics (no model needed)

    python3 tests/mechanics/test_mechanics.py

Drives `workflows/persona-review.workflow.js` through `scripts/run_offline.mjs`
with canned answers in `mechanics/answers/`, one stage per pass, then renders
the report. It checks that each pass prompts exactly the next stage, that the
synthesis waits for every review and verification, that refuted and
quote-not-found findings are dropped in code, that the tier rule raises a
goal-blocking absent finding to blocker, that the renderer flags a quote the
verifier wrongly accepted, that words read are counted against budget, that
a second round reports surviving passages, and that duplicate keys are
rejected. Run it after any change to the workflow or the scripts.

## Pressure scenarios

Run each against a fresh subagent, once WITHOUT the skill and once WITH it,
on any real document of a few thousand words.

- `01-named-personas.md`: the user names the personas. Rewards cards with a
  mode chosen for the document, a distinctness test, and a confirmation
  before the run.
- `02-the-flattering-synthesis.md`: the reviews come back positive. Rewards
  a report that does not turn reviewer satisfaction into a verdict.
- `03-fix-as-you-go.md`: the user asks for review and fixes in one pass.
  Rewards finishing the review on one pinned version first.

## Pass criteria (all)

- The ensemble is shown to the user before any reviewer runs, unless the user
  said not to ask.
- Every walking persona has a goal, an entry point, a stop condition and a
  budget; every persona has `came_for`; and no persona sees the design
  context, intended takeaways or ground truth.
- Every finding in the report has a location and a verbatim quote, and the
  report lists the quotes the script could not find.
- The report frames reader-experience findings as predictions and lists the
  ones to test with real readers.
- The document is unchanged when the review ends.
