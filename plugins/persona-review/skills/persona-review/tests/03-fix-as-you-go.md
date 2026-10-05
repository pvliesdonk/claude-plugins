# Test 3: Review and fix in one pass

## Scenario

User says: "Persona-review the docs/ site and fix whatever the personas find
as you go, I want it done today."

## Baseline failure (without the skill)

The first reviewer's findings are fixed before the second reviewer runs. The
later personas read a different site from the earlier ones, the diff mixes
eight readers' fixes with no record of which finding caused which change,
and nothing can be compared in a second round.

## Expected output (with the skill)

The review runs to completion on one pinned version, and the document is
unchanged when it ends. Then the hand-over gives the priorities and asks
which to fix; fixes follow as separate changes, each tied to the finding it
answers. If the user wants confirmation that the fixes worked, a second
round runs with the same ensemble and `--previous`.

Pass criteria:
- `pin` is set, and `git status` shows no change to reader files after the
  review.
- No fix lands before the report exists.
- The hand-over offers a second round rather than declaring the fixes
  verified.
