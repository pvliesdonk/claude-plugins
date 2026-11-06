# Triage Mechanics: GitLab (glab, glab api, MCP)

The GitLab counterpart of [mechanics.md](mechanics.md). Same disciplines, different
traps. Works for gitlab.com and for any self-managed instance; nothing here assumes
a hostname.

Verified against the GitLab REST API v4 and `glab` documentation as of GitLab 19.x
and glab 1.128. Self-managed instances lag: **read the instance version first** and
treat any feature below marked with a version as absent until you have checked.

## Step 0: Which instance, which version, which tier

Three facts decide which commands below exist for you. Establish them before triage,
and say them in your output.

```bash
git remote get-url origin          # the host is whatever this says; never assume gitlab.com
glab auth status                   # which hosts glab is authenticated against
# For a self-managed host glab is not yet logged in to:
#   glab auth login --hostname gitlab.example.com
# glab picks the host from the git remote; GITLAB_HOST overrides it.

glab api metadata | jq '{version, enterprise, plan}'
```

- `enterprise: false` means Community Edition: **Free-tier features only**, whatever
  anyone tells you.
- `plan` names the licence (`free`, `premium`, `ultimate`). It is `null` on gitlab.com,
  where licences are per namespace, and older instances may not return it at all. When
  you cannot read the tier, probe the feature you need (for example, list a group's
  epics) and treat a 403/404 as "not available here".

Tier-gated features this file touches:

| Feature | Tier | Consequence for triage |
|---|---|---|
| Scoped labels (`key::value`) are mutually exclusive | Premium, Ultimate | On Free, `priority::high` is just a name containing colons |
| `blocks` / `is_blocked_by` issue links | Premium, Ultimate | On Free, only `relates_to` exists: no direction |
| Epics | Premium, Ultimate | On Free, there is no epic object at all |
| Default description template in project settings | Premium, Ultimate | Invisible in the repository |
| Child tasks under an issue | Free and up | Available everywhere |
| Archived labels | GA in 18.11 (flagged from 18.3) | Older instances: retire by colour and description instead |

## Capability Matrix

| Operation | `glab` CLI | `glab api` | GitLab MCP |
|---|---|---|---|
| List labels | `glab label list` (⚠️ `--per-page` defaults to 30) | ✅ with counts | depends on instance version |
| Create / edit / delete label | `glab label create/edit/delete` | ✅ | check the server's tool list; assume ❌ |
| Add / remove labels on an issue | `glab issue update --label/--unlabel` (additive) | `add_labels` / `remove_labels` (additive); `labels` **replaces** | `labels` replaces; `add_labels`/`remove_labels` from 19.4 |
| List / create milestones | `glab milestone list/create` (⚠️ list defaults to 20) | ✅ | read only |
| Set milestone on an issue | `--milestone <title>` | `milestone_id` = **global ID**, not the iid | `milestone_id` |
| Close with a reason | ❌ no reason field exists | ❌ | ❌ |
| Mark duplicate | quick action in a note: `/duplicate #N` | same, via notes API | ❌ |
| Directed dependency | ❌ | issue links API, Premium | ❌ |
| Search | `glab issue list --search` (title/description text) | search API | `search` |

GitLab's MCP server lives at `https://<host>/api/v4/mcp` (from 18.4). Its tool set has
already been renamed once: `get_issue` / `create_issue` were superseded by
`get_work_item` / `save_work_item` in 19.4. **Read the tool list the server actually
gives you**; never call a tool name from memory or from this file.

## ⚠️ Four Traps

**1. A typo creates a label.** `add_labels`, `labels`, and therefore
`glab issue update --label`, create a new *project* label when the name does not
exist. `--label "area::serach"` succeeds, and you have just added a label to the
taxonomy during a sweep, which is the one thing triage must not do. Match every name
against the live list before applying it. The API also accepts names, not IDs, so
there is no type check to save you.

**2. On Premium, a scoped label replaces its siblings silently.** Adding
`priority::high` to an issue carrying `priority::low` removes `priority::low`, with no
error and no prompt. So adding a scoped label is never purely additive: on the
priority axis it is a priority *change*, which belongs in the confirm tier even when
the command looks like an add. On Free the same command leaves both labels on the
issue, and the "one priority" contract is enforced by nobody.

**3. Group labels make every blast radius group-wide.** A label defined on a group is
inherited by every subgroup and project under it. Renaming, recolouring or deleting it
from one project's triage changes every project in the group. `is_project_label` in the
API response tells you which kind you are looking at; check it before any edit.
**Promoting** a project label to a group label is irreversible, and it merges every
same-named label in the group's other projects into it.

**4. iid versus id.** Issues have a project-scoped `iid` (the `#123` humans see) and a
global `id`. Project-scoped endpoints take the iid; `milestone_id` takes the
milestone's *global* ID, not its iid and not its title. Look it up first.

## Discovery

```bash
# Labels, with counts and the project/group distinction. Paginate: the API caps a page at 100.
glab api --paginate "projects/:fullpath/labels?with_counts=true&include_ancestor_groups=true" \
  | jq -r '.[] | [.name, (if .is_project_label then "project" else "GROUP" end),
                  "open=\(.open_issues_count)", "closed=\(.closed_issues_count)",
                  "mr=\(.open_merge_requests_count)"] | @tsv'

# The glab shorthand truncates exactly like gh does: --per-page defaults to 30.
glab label list --per-page 100

# Templates. GitLab templates are plain Markdown; there are no YAML forms.
ls .gitlab/issue_templates/ .gitlab/merge_request_templates/ 2>/dev/null
# Labels a template applies are quick actions inside it — the canonical type vocabulary:
grep -Hn '^/label' .gitlab/issue_templates/*.md 2>/dev/null
# Templates inherited from the group or instance do NOT appear in the repo. List them all:
glab api "projects/:fullpath/templates/issues" | jq -r '.[].name'

# Milestones: project and group ones are different objects. List both.
glab milestone list --per-page 100 --output json \
  | jq -r '.[] | "\(.id)\t\(.iid)\t\(.title)\tstart=\(.start_date)\tdue=\(.due_date)"'
glab milestone list --group GROUP --include-ancestors --per-page 100   # group milestones the project can use
# Older glab has no `milestone` command; use: glab api --paginate "projects/:fullpath/milestones"

# Anything that emits or depends on a label name
grep -rln -e 'labels' .gitlab/ .gitlab-ci.yml .triage-policies.yml renovate.json 2>/dev/null
```

Two more label consumers live outside the repo and break silently:

- **Issue board lists** are bound to labels. Deleting a label removes the board list
  built on it; renaming changes the column everyone looks at.
- **Bots**: `gitlab-triage` reads `.triage-policies.yml`, Renovate reads
  `renovate.json`, and CI jobs may call the API. Rename a label they emit without
  changing their config and they recreate the old one.

## Triage Queries

```bash
glab issue list --per-page 100 --not-label "priority::high,priority::medium,priority::low"
glab api --paginate "projects/:fullpath/issues?state=opened&milestone=None"   # no milestone
glab api --paginate "projects/:fullpath/issues?state=opened&labels=None"   # no label at all
glab issue list --per-page 100 --order updated_at --sort asc                # staleness: look, don't close
```

`--per-page` caps at 100. For anything larger use `glab api --paginate` rather than
trusting one page. `glab issue list` defaults to open issues; `--all` includes closed.

## Applying Triage

```bash
# Additive and safe — but every name must already exist (trap 1)
glab issue update 123 --label bug,area::search --unlabel enhancement

# Milestone by title; empty string removes it
glab issue update 123 --milestone "v4.1"
glab issue update 123 --milestone ""

# Raw API: add_labels/remove_labels are additive; labels= REPLACES the whole set
glab api -X PUT "projects/:fullpath/issues/123" -f add_labels="area::search" -f remove_labels="enhancement"

# Milestone by global ID through the API
MID=$(glab milestone list --per-page 100 --output json | jq -r '.[] | select(.title=="v4.1") | .id')
glab api -X PUT "projects/:fullpath/issues/123" -f milestone_id="$MID"
```

## Closing

GitLab has **no close reason**. An issue is open or closed; why lives in the comment,
and in a label only if the project has one for it. That makes the comment mandatory,
not courtesy.

```bash
# Duplicate: the quick action closes AND links. Quick actions run in notes posted via the API.
glab issue note 300 -m "/duplicate #250"

# Completed: comment first, then close
glab issue note 225 -m "Delivered by !880: GraphFacet.get_neighborhood() (facets/graph.py:314)."
glab issue close 225

# Won't fix: same shape. Apply the project's won't-fix label only if one already exists.
glab issue note 310 -m "Not planned: superseded by the 4.0 release model; no forward consequence."
glab issue close 310
```

Merge requests are `!N`, issues `#N`, milestones `%"title"`, labels `~"name"`, epics
`&N`. Use the sigil, not prose, so the reference becomes a link.

## Dependencies and Hierarchy

```bash
# Directed link (Premium+): this issue is blocked by #859
glab api -X POST "projects/:fullpath/issues/809/links" \
  -f target_project_id="GROUP%2FPROJECT" -f target_issue_iid=859 -f link_type=is_blocked_by

# The same as a quick action (Premium+). On Free only /relate works, and it carries no direction.
glab issue note 809 -m "/blocked_by #859"

# Read what is linked
glab api "projects/:fullpath/issues/809/links" | jq -r '.[] | "\(.link_type)\t#\(.iid)\t\(.title)"'
```

On Free, `/blocked_by` and `link_type=blocks` are unavailable and only `relates_to`
can be created. An undirected link does not carry order; do not present it as if it
did.

## Bootstrapping a Taxonomy

A new GitLab project has **no labels at all**: there is no seeded default set as on
GitHub. It may still inherit group labels, so list with `include_ancestor_groups=true`
before concluding it is empty. If the group already defines a type axis, use it; a
project-level `bug` beside a group-level `bug` is a duplicate in every picker.

```bash
glab label create --name bug     --color "#d73a4a" --description "Something isn't working"
glab label create --name feature --color "#a2eeef" --description "New capability or request"
```

`glab label create` is not an upsert: it fails if the label exists. Check first.

Scoped labels (`type::bug`) only buy exclusivity on Premium. On Free they are just
longer names; use them only if the project already does, or if a move to Premium is
planned and stated.

## Curating an Existing Taxonomy

```bash
# Snapshot first — this is destructive work
glab api --paginate "projects/:fullpath/labels?with_counts=true&include_ancestor_groups=true" > /tmp/labels-before.json

# Blast radius is in the snapshot: open_issues_count, closed_issues_count, open_merge_requests_count.
# The counts do NOT include closed or merged MRs. Count those separately before deleting:
glab api --paginate "projects/:fullpath/merge_requests?state=all&labels=enhancement" | jq length

# RENAME preserves assignments. Project label:
glab api -X PUT "projects/:fullpath/labels/ci" -f new_name="area::ci" -f description="CI, release machinery"
# Group label — this renames it in EVERY project of the group. Confirm that explicitly:
glab api -X PUT "groups/GROUP%2FSUBGROUP/labels/ci" -f new_name="area::ci"

# RETIRE in place. From 18.11 (GA) labels can be archived: hidden from pickers, kept on history.
glab api -X PUT "projects/:fullpath/labels/future" -f archived=true
# Before 18.11, or if the call is rejected: grey it and say so.
glab api -X PUT "projects/:fullpath/labels/future" -f color="#cccccc" -f description="RETIRED — no milestone is the backlog"
```

**Deleting a label removes it from every issue and merge request, open and closed, and
cannot be undone** (GitLab user documentation, *Delete a label*). The glab
documentation for `glab label delete` says the opposite: that the label stays on
issues that use it. Act on the server's documentation, the more destructive reading,
and never cite glab's text as permission to delete. Archived labels exist precisely so
that you do not need to.
