# Triage Mechanics: gh, gh api, and MCP

Three tool paths reach the same API. Pick by what the operation needs — the CLI cannot do everything, and the API/MCP path has two traps that silently destroy data.

All commands verified against `gh` 2.97.0 and the GitHub REST API (2022-11-28).

## Capability Matrix

| Operation | `gh` CLI | `gh api` | GitHub MCP |
|---|---|---|---|
| List / read labels | `gh label list` | ✅ | `get_label` (one label, by exact name — no listing) |
| Create / edit / delete label | `gh label create/edit/delete` | ✅ | ❌ |
| Add / remove labels on an issue | `gh issue edit --add-label/--remove-label` | ⚠️ replaces the whole set | ⚠️ `issue_write` replaces the whole set |
| List / create milestones | ❌ **no `gh milestone` command** | ✅ | ❌ |
| Set milestone on an issue | `--milestone <title>` | by **number** | `issue_write` by **number** |
| Close with reason | `gh issue close --reason` | ✅ | `issue_write` `state_reason` |
| Native sub-issue link | `gh issue edit --add-sub-issue` | ✅ | `sub_issue_write` |
| Semantic duplicate search | ❌ | ❌ | `search_issues` (natural language) |

**Rule of thumb:** `gh` for issue-level edits, `gh api` for milestones and anything the CLI lacks, MCP for reading and for semantic duplicate hunting.

## ⚠️ Two Traps in the API / MCP Path

**1. `labels` replaces, it does not append.** The REST docs for *Update an issue* say: *"Pass one or more labels to replace the set of labels on this issue."* So MCP's `issue_write` with `labels: ["bug"]` **wipes every other label on the issue**. The `gh` CLI's `--add-label` / `--remove-label` are additive and are the safe path for incremental triage. If you must use MCP, read the current labels first and send the full intended set.

**2. `milestone` takes a number, not a title.** `gh issue edit --milestone "v4.1"` takes the title; the REST API and MCP's `issue_write` take the milestone *number*. Look it up first — passing a title silently fails or errors.

## Discovery

```bash
# ALWAYS pass --limit: both commands default to 30, and labels sort by creation date,
# so the bare form hides the newest labels — exactly the ones triage needs.
gh label list --limit 200
gh label list --limit 200 --json name,color,description,isDefault

# The canonical type vocabulary comes from the issue forms, not from the label list
grep -H 'labels:' .github/ISSUE_TEMPLATE/*.yml

# Milestones — no gh command exists for these
gh api repos/:owner/:repo/milestones --jq '.[]|"\(.number)\t\(.title)\topen=\(.open_issues)\tclosed=\(.closed_issues)"'

# Issue types (org-only feature; 404 on user-owned repos).
# If present, type belongs there, NOT in a label.
gh api repos/:owner/:repo/issues/types --jq '.[].name'
```

## Triage Queries

```bash
R=OWNER/REPO

gh issue list --repo $R --state open --limit 200 --search "no:milestone"
gh issue list --repo $R --state open --limit 200 --search "no:label"
gh issue list --repo $R --state open --limit 200 \
  --search '-label:priority:low -label:priority:medium -label:priority:high'
gh issue list --repo $R --state open --limit 200 --search "sort:updated-asc"   # staleness: look, don't close

# Untriaged by any axis — the real inbox
gh issue list --repo $R --state open --limit 200 --json number,title,labels \
  --jq '.[]|select([.labels[].name]|map(startswith("priority:"))|any|not)|"#\(.number)\t\(.title)"'
```

## Applying Triage

```bash
# One issue, several axes. --add-label/--remove-label are additive and safe.
gh issue edit 123 --repo $R --add-label bug --add-label area:search --remove-label enhancement

# gh issue edit accepts MULTIPLE issue numbers — no loop needed for a shared change
gh issue edit 101 102 103 --repo $R --add-label area:index

# Milestone by title (CLI only); removal has its own flag
gh issue edit 123 --repo $R --milestone "v4.1"
gh issue edit 123 --repo $R --remove-milestone

# Native sub-issue link (epics). CLI takes the number:
gh issue edit 809 --repo $R --add-sub-issue 859
# The raw API takes the child's DATABASE ID, not its number:
CHILD=$(gh api repos/$R/issues/859 --jq .id)
gh api -X POST repos/$R/issues/809/sub_issues -F sub_issue_id="$CHILD"
```

## Closing

```bash
gh issue close 225 --repo $R --reason completed \
  --comment "Delivered by #880: GraphFacet.get_neighborhood() (facets/graph.py:314)."

gh issue close 300 --repo $R --reason duplicate --duplicate-of 250

gh issue close 310 --repo $R --reason "not planned" \
  --comment "Superseded by the 4.0 release model; no forward consequence."
```

Valid reasons: `completed`, `not planned`, `duplicate`. The API spells the middle one `not_planned`.

## Milestones

No `gh milestone` command exists — all of this is `gh api`.

```bash
gh api repos/$R/milestones -f title="v4.2" -f state=open \
  -f description="Release payload for 4.2" -f due_on="2026-10-01T00:00:00Z"

# Look up the number before using the API/MCP path to set one
NUM=$(gh api repos/$R/milestones --jq '.[]|select(.title=="v4.2")|.number')

gh api -X PATCH repos/$R/issues/123 -F milestone="$NUM"
gh api -X PATCH repos/$R/issues/123 -F milestone=null      # remove

# Close a milestone when its release ships — this is the audit trail
gh api -X PATCH repos/$R/milestones/$NUM -f state=closed
```

## Bootstrapping a Taxonomy

GitHub seeds nine defaults on every new repo: `bug`, `documentation`, `duplicate`, `enhancement`, `good first issue`, `help wanted`, `invalid`, `question`, `wontfix`. Confirm what is actually there — `isDefault` marks the untouched ones:

```bash
gh label list --limit 200 --json name,isDefault --jq '.[]|select(.isDefault)|.name'
```

`duplicate`, `invalid` and `wontfix` duplicate the native `state_reason` values and can stay unused.

`gh label create --force` is an idempotent upsert — safe to re-run, and the right shape for a checked-in bootstrap script:

```bash
gh label create bug     --color d73a4a --description "Something isn't working"           --force
gh label create feature --color a2eeef --description "New capability or request"          --force
gh label create docs    --color 0075ca --description "Documentation only"                 --force
gh label create chore   --color ededed --description "Maintenance, no user-facing change" --force
```

Add area and priority labels only when you can name the query they answer. Do not scaffold an axis in advance.

## Curating an Existing Taxonomy

```bash
# Snapshot first — this is destructive work
gh label list --limit 200 --json name,color,description > /tmp/labels-before.json

# RENAME preserves every existing assignment. Delete-then-create loses them all.
gh label edit ci --name area:ci --color 1d76db --description "CI, release machinery, workflows"

# BLAST RADIUS before any delete — --state all, and PRs are counted separately
for l in enhancement test future; do
  printf '%-24s issues=%s prs=%s\n' "$l" \
    "$(gh issue list --repo $R --state all --label "$l" --limit 500 --json number --jq length)" \
    "$(gh pr    list --repo $R --state all --label "$l" --limit 500 --json number --jq length)"
done

# MERGE = migrate first, then delete. gh issue list does not return PRs, hence both loops.
merge() {  # merge $1 into $2
  gh issue list --repo $R --state all --label "$1" --limit 500 --json number --jq '.[].number' \
    | xargs -r -I{} gh issue edit {} --repo $R --add-label "$2" --remove-label "$1"
  gh pr list --repo $R --state all --label "$1" --limit 500 --json number --jq '.[].number' \
    | xargs -r -I{} gh pr edit {} --repo $R --add-label "$2" --remove-label "$1"
  gh issue list --repo $R --state all --label "$1" --limit 5   # verify empty BEFORE deleting
}

gh label delete enhancement --repo $R --yes   # only after the verify above returns nothing
```

Deleting a label removes it from **closed** issues too. Prefer leaving a dead label unused.

Before renaming anything, check nothing emits it:

```bash
grep -rn "enhancement" .github/ renovate.json 2>/dev/null
```

Form-owned (`.github/ISSUE_TEMPLATE/*.yml`) and bot-owned (`renovate.json`, workflows) labels must be changed in their config in the same commit, or the emitter recreates the old name alongside the new one.

## MCP Path

```jsonc
// Read — safe, and the only semantic duplicate search available
issue_read      { method: "get", owner, repo, issue_number }
issue_read      { method: "get_labels", owner, repo, issue_number }
search_issues   { query: "search returns empty after restart", owner, repo }
list_issues     { owner, repo, state: "OPEN", labels: ["bug"], perPage: 100 }

// Write — labels REPLACES the set; milestone is a NUMBER
issue_write     { method: "update", owner, repo, issue_number,
                  labels: ["bug","area:search"],   // full intended set, not a delta
                  milestone: 4 }

issue_write     { method: "update", owner, repo, issue_number,
                  state: "closed", state_reason: "duplicate", duplicate_of: 250 }

sub_issue_write { method: "add", owner, repo, issue_number: 809, sub_issue_id: <database id> }
```

`list_issues` paginates by cursor (`after` ← previous response's `pageInfo.endCursor`); `perPage` maxes at 100. Pass `fields` to drop `body` on large sweeps.
