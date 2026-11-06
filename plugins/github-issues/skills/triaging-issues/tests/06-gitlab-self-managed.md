# Test 6: GitLab, self-managed, group labels and scoped priority

## Status: NOT YET RUN — the baseline below is predicted, not observed

Run it once without the skill and once with it before relying on it, and replace the
predicted baseline with what the run actually produced.

## Scenario

User says: "Triage the open issues in `platform/ingest` on our GitLab
(`git.example.internal`). Set priorities where they're obvious and tidy up the
labels — `prio::high` and `priority::high` both exist, merge them."

Sandbox: `glab` is unauthenticated; the deliverable is the commands the agent WOULD
run. Supplied as fixtures:

- `glab api metadata` → `{"version": "17.9.2-ee", "enterprise": true, "plan": "premium"}`
- labels (from the API, `include_ancestor_groups=true`):
  - `bug`, `feature`, `priority::high`, `priority::low` — `is_project_label: false` (group `platform`, 14 projects)
  - `prio::high` — `is_project_label: true`, 6 open / 41 closed issues, 3 open MRs
  - `area::ingest` — project label
- `.gitlab/issue_templates/` does not exist in the repo; the templates API lists
  `Bug` and `Feature` (inherited from the group), and `Bug` contains `/label ~bug`
- 12 open issues; issue #31 already carries `priority::low` and its body reports data
  loss on restart

## Predicted baseline failure

- Uses `ls .gitlab/issue_templates/`, concludes there are no templates, and invents a
  type vocabulary
- `glab label list` bare (30-item default) or no listing at all
- Applies `priority::high` to #31 as an "add", not noticing it silently removes
  `priority::low` on Premium
- Merges by renaming `priority::high` (a **group** label) or deleting `prio::high`
  without counting closed issues and MRs
- Archives or recolours a group label from a project-scoped task
- Applies a mistyped label (`area::injest`), creating a new label mid-sweep

## Pass criteria

- States host, version (17.9), edition and tier (Premium) before proposing anything
- Reads the inherited templates via the API and takes `bug` / `feature` from them
- Lists labels with pagination or `--per-page 100`, never bare
- Puts every priority change, including the one on #31, in the confirm tier and names
  the scoped-label replacement as the reason
- Treats the merge as curation, separate from the sweep: migrate `prio::high` →
  `priority::high` with `add_labels`/`remove_labels` on issues AND MRs (open and
  closed), verify zero, and only then propose deleting the project label
- Does not edit, rename or archive any group label; flags that doing so touches 14
  projects
- Does not propose archiving: 17.9 predates GA of archived labels (18.11); falls back
  to grey + RETIRED description if retirement is wanted
- Every applied label name appears in the fixture list
