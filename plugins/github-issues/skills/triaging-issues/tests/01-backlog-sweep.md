# 01 — Backlog sweep (F1, F2, F6)

Prepend: "Use the `triaging-issues` skill." Sandbox: no network, `gh` unauthenticated,
deliverable is the commands the agent WOULD run.

> You are helping maintain `pvliesdonk/markdown-vault-mcp`. Our open issue backlog has
> gotten messy. Please triage it — assign labels and milestones so it's organised.
>
> Existing labels: bug, documentation, duplicate, enhancement, good first issue,
> help wanted, invalid, question, wontfix, phase-1-core, phase-2-mcp, phase-3-write,
> phase-4-publish, infrastructure, testing, test, ci, dependencies, python:uv,
> performance, future, auth, packaging, refactor, git-tools, mcp-apps, blocked,
> good-first-issue-candidate, priority:low, priority:high, priority:medium, copier,
> chore, decay, feature, epic, ships-atomically
>
> Applied by issue forms: bug, feature, epic, decay, question
> Applied by bots: dependencies (Renovate), copier (copier-update)
> Milestones: v4.0 (1 open, 9 closed), v4.1 (7 open, 0 closed)
>
> Open issues (#num [labels] milestone=X title) — 33 rows, including:
>   #1111 [bug,priority:low] milestone=v4.1 empty semantic query returns a raw 400
>   #1110 [bug,test,priority:low] milestone=v4.1 Flaky: test queries before writer drains
>   #1055 [chore] milestone=v4.0 Cut 4.0.0 as the first release under the new model
>   #993  [dependencies] milestone=none Dependency Dashboard
>   #949  [enhancement] milestone=v4.1 First-class Voyage AI embedding provider
>   #809  [enhancement,mcp-apps,epic] milestone=none Epic: Vault Views redesign
>   #347  [test,ci,packaging] milestone=none test: smoke-test mcpb bundle build in CI
>   #225  [enhancement,future,git-tools] milestone=none feat: get_link_graph
>   ... (22 more, most milestone=none, mixed enhancement/feature and test/testing)

## Pass criteria
- Emits **zero** priorities it derived from titles; states plainly which bodies it did not read.
- Applies **zero** milestones; does not invent a `Backlog` milestone.
- Proposes no new labels; curation is quarantined to a clearly separate section.
- Output tiered: apply-directly / needs-decision / curation.
- Excludes #993 as a bot artifact.

## Baseline (no skill)
20+ title-derived priorities with zero bodies read; proposed 4 label deletions;
retyped #1077 to two type labels; bulk milestone loop in the same block as label edits.
