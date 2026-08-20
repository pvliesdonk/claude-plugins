# Pressure scenarios for `code-archaeology`

Run each against a fresh subagent in a real repository, once WITHOUT the skill and once
WITH it. Constrain the agent to `git` and `gh` only — the point is the general method,
not whatever code-intelligence tooling a particular repo happens to have. Read-only.

## The baseline failure these were written from

Both baseline runs produced genuinely excellent answers: right commits, right PRs,
rejected alternatives, a careful verified-versus-inferred split. One found that a
breaking-change changelog entry had been destroyed by a later mechanical regeneration.

Both were working in a **shallow clone** and neither noticed. Every key commit they
cited was unreachable from `HEAD`, present only because tags held the objects:

    7b2496d7 exists=commit reachable-from-HEAD=NO   (introduced the var)
    f82fd60b exists=commit reachable-from-HEAD=NO   (renamed it)
    ec77fc44 exists=commit reachable-from-HEAD=NO   (implemented the decision)

    -S READY_TIMEOUT   HEAD-only: 2 hits   --all: 13 hits
    -S bucket in src/  HEAD-only: 3 hits   --all: 27 hits

The failure is not weak evidence. It is **unestablished completeness** — and both runs
then made negative and superlative claims ("never appeared in any released version",
"zero hits, all tags") that the documented method did not support.

## Scenarios

- `01-reconstruct-a-decision.md` — why does a tool behave this way, who decided, what
  was rejected. Rewards finding the design discussion, not just the implementing commit.
- `02-trace-a-vanished-symbol.md` — an env var referenced in an old doc no longer works.
  Rewards following a rename by content rather than by path, and checking whether the
  change was ever announced.

## Pass criteria (both)

- Runs the ground-truth check **before** any history query, and says what it found.
- Names the scope of each search (`HEAD` vs `--all`) rather than leaving it implicit.
- Any negative or superlative claim is either backed by a stated completeness argument,
  or weakened to what was actually observed.
- Uses more than one pull-request-to-issue index where the first returns nothing.
- Distinguishes verified from inferred, and says "not recorded" rather than
  reconstructing a plausible rationale.
