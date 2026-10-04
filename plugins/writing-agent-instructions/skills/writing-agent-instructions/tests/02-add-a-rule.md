# Test 2: A new rule arrives with its history

## Scenario

User says: "Add a rule to AGENTS.md that PR titles must be conventional
commits. We got bitten: knope silently drops a release entry when the type
isn't one it counts, no warning, and the changelog came out with a hole."

## Baseline failure (without the skill)

The paragraph as it stands in the file today, model-authored in an earlier
session:

```markdown
**Pull-request titles are enforced, not merely encouraged.** A squash merge
takes the PR title as the commit subject, so CI's `PR Title` job checks it
against the type list above and fails the `CI Success` aggregate when it does
not match. This is not style policing: knope computes versions and writes
`CHANGELOG.md` from those subjects, and it silently ignores a subject whose
type it does not count — no fallback heading, no entry, no warning. That
silent-drop class is exactly what the gate exists for: it keeps the history
parseable and the accepted set deliberate.
```

Failure modes present:
- One directive in five sentences, and it is implicit ("checks it against
  the type list").
- Enforcement narrative (what the job does, what the aggregate does) that the
  job's own failure message already carries.
- Justification to a human ("this is not style policing") that decides
  nothing for the agent.
- Bold emphasis added to a file that already has a dozen bold lines.

## Expected output (with the skill)

```markdown
- PR title: `type(scope): subject` with `type` one of build, chore, ci, docs,
  feat, fix, perf, refactor, revert, style, test. Only `feat`, `fix` and `!`
  reach the changelog; a title with any other type ships without an entry.
```

And in the change description: the knope silent-drop story goes to the `PR
Title` job's failure annotation or to CONTRIBUTING.md, with the file named.

Pass criteria:
- One or two sentences, both directives or scope limits.
- The one clause of rationale kept is the one that decides an unlisted case
  (which types reach the changelog), not the one that justifies the gate.
- No new bold; the rule sits in the section that owns commit conventions.
- The history is sent somewhere named, not dropped silently and not kept.
