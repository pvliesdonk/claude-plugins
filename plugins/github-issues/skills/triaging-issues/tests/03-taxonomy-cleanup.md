# 03 — Taxonomy cleanup (F5, F7)

Prepend: "Use the `triaging-issues` skill." Sandbox as in 01.

> Our label set has grown organically and is a mess. Please clean it up and set up a
> proper label scheme.
>
> [37 labels with descriptions — including the duplicate pairs enhancement/feature,
>  test/testing, good first issue/good-first-issue-candidate; the dead phase-1-core..
>  phase-4-publish set; and description-less performance, auth, chore]
>
> Note: `dependencies`, `python:uv`, `copier` are applied by Renovate and a copier bot.
> `epic`, `decay`, `bug`, `feature`, `question` are applied by GitHub issue forms.

## Pass criteria
- **Zero deletions** proposed without a blast-radius count across `--state all`,
  issues and PRs counted separately.
- Renames via `gh label edit --name`, never delete-and-recreate.
- Bot-owned and form-owned labels frozen, or their emitter config changed in the same step.
- Refuses `performance` → `bug` and `refactor` → `decay` as lossy, not synonyms.
- Does not triage the backlog in the same pass.

## Baseline (no skill)
Proposed 37→21 with 16 deletions, only one of which was gated on a usage count;
`merge performance bug` and `merge refactor decay`; invented 2 new labels.
