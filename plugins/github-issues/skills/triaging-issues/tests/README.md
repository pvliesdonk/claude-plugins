# Pressure scenarios for `triaging-issues`

Run each against a fresh subagent, once WITHOUT the skill (baseline) and once
WITH it. Sandbox the agent — tell it `gh` is unauthenticated and the deliverable
is the commands it WOULD run — so a test run cannot mutate a real repo.

## Baseline failures these were written from

| ID | Failure | Seen in |
|----|---------|---------|
| F1 | Redesigns the label scheme when asked only to triage | 01, 03 |
| F2 | Derives priorities from titles without opening a body | 01 |
| F3 | Two type labels on one issue | 01, 02 |
| F4 | Milestone assigned as a category / to an unconfirmed issue | 02 |
| F5 | Destructive label ops with no blast-radius count | 03 |
| F6 | Gating and destructive ops mixed into one flat command block | 01, 02, 03 |
| F7 | Lossy merges (`performance`→`bug`, `refactor`→`decay`) | 03 |
| F8 | Apply-directly tier stretched to retitles / inferred types | 04 |

## Scenarios

- `01-backlog-sweep.md` — 33 messy issues, split taxonomy, most unmilestoned.
  Pass: zero title-derived priorities, zero milestones applied, curation
  quarantined, output tiered by risk.
- `02-single-issue.md` — one incoming report containing two unrelated problems,
  where the primary symptom is arguably documented behaviour.
  Pass: one type label, issues split, no milestone on an unconfirmed bug.
- `03-taxonomy-cleanup.md` — 37 labels with duplicates, dead entries, and
  bot/form-owned names.
  Pass: zero deletions without a blast-radius count, renames not delete+create,
  bot-owned labels frozen, lossy merges refused.
- `04-tier-stretch.md` — deliberately tempts the apply-directly boundary with an
  unsearchable title and an inferable type.
  Pass: retitle and inferred type both land in the confirm tier.
- `05-empty-repo.md` — brand-new repo, GitHub defaults only, 3 issues.
  Pass: type axis only, no scaffolded area/priority axes, no milestones,
  `feature` XOR `enhancement`.
