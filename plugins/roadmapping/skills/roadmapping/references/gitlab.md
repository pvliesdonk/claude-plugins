# Roadmapping on GitLab

Read this before charting or refining on GitLab, hosted or self-managed. The model in
`SKILL.md` (milestone as epic, refinement issue, dependency graph, index in the repo)
carries over. Three of its mechanisms do not carry over unchanged, and one GitLab
feature actively pulls against a stop rule.

## First: establish the instance

```bash
git remote get-url origin                       # the host; never assume gitlab.com
glab api metadata | jq '{version, enterprise, plan}'
```

`enterprise: false` is Community Edition, which is Free tier. Otherwise probe the
feature you need (list the group's epics; create nothing) and read a 403/404 as
absent. `plan` is recent, missing on older instances and `null` on gitlab.com, so use
it to confirm the probe, not to replace it. Record host, version and tier in the medium stanza alongside
where the index and milestones live: the next session needs them before it can trust
any command.

## Which object is the roadmap's epic

`SKILL.md` calls the epic a *milestone* because that is the only object GitHub offers.
GitLab offers two candidates, and which one to use is a decision for the user, not a
default for you. Ask, then record the answer in the stanza.

| | Milestone as epic | GitLab epic as epic (Premium+) |
|---|---|---|
| Lives at | project or group | group only |
| Holds | issues, merge requests | child issues, child epics |
| Frees milestones for | nothing; the release-payload conflict in `SKILL.md` applies in full | release payloads, so both conventions can coexist |
| Refinement issue | required, as written | still required: an epic with no children reports nothing honestly either |
| Acceptance criterion | in the milestone description | in the epic description |

With group epics, the refinement issue still has to live in a project, because epics
are group-level and issues are not. Put it in the project that holds the index, attach
it to the epic as a child, and record that choice in the stanza.

On Free there is no choice: milestone as epic. On Premium+, the epic option removes
the one structural conflict `SKILL.md` warns about, at the price of the roadmap living
at group level. Either way, everything below about refinement issues, frozen criteria
and derived resolution applies unchanged.

**Group or project milestones.** A roadmap spanning several projects needs group
milestones (or epics); a single-project roadmap can use project milestones. Do not mix
both for one roadmap: an agent then has to guess which list is authoritative.

## Dates: the stop rule under pressure

The rule is: **never set a milestone due date.** GitLab pushes harder against it than
GitHub does.

- GitLab milestones carry both a **start date and a due date**, and the milestone page
  draws a burndown chart from them. Set neither. A start date implies an order just as
  a due date does.
- GitLab epics have start and due dates, either fixed or *inherited* from their
  children's milestones. An inherited date is still a date: if features land in
  timeboxed milestones, the epic acquires a schedule nobody chose. Check the epic's
  dates after refinement and say what you found.
- The **Roadmap view** (Premium+) draws epics on a timeline and only shows epics that
  have dates. It is tempting to add dates "so the roadmap shows up". That converts the
  set of intentions into a schedule, which is exactly what the rule forbids. The index
  is the roadmap; the Roadmap view is a Gantt chart with a better name. Say so if the
  user asks for it, and let them decide.
- **Iterations** (Premium+) are GitLab's timebox object. If the project uses them, a
  refined, ready feature can enter an iteration; that is delivery planning and no
  longer this skill's business. A refinement or research issue in an iteration is
  fine; an epic or a milestone used as an iteration is not.

## The graph: directed edges are a paid feature

`SKILL.md` puts order in the dependency graph. On GitLab, directed issue links
(`blocks` / `is blocked by`) exist on **Premium and Ultimate only**.

**Premium+:**

```bash
# refine-B (#42) is blocked by feature X in milestone A (#17)
glab issue note 42 -m "/blocked_by #17"
# or through the API, which also works across projects
# target_project_id: numeric ID (or plain group/project) in the body, never %2F
glab api -X POST "projects/:fullpath/issues/42/links" \
  -f target_project_id="$(glab api "projects/:fullpath" | jq .id)" -f target_issue_iid=17 -f link_type=is_blocked_by
# read the edges
glab api "projects/:fullpath/issues/42/links" | jq -r '.[] | "\(.link_type)\t#\(.iid)\t\(.title)"'
```

Blocked issues carry a blocked icon in lists and boards. Do not assume an equivalent
of GitHub's `is:blocked` search qualifier; until you have confirmed one on this
instance, a bottleneck query reads the links API per issue.

**Free:** only `relates_to` exists, and it has no direction. The graph `SKILL.md`
relies on **cannot be expressed natively.** Do not paper over that:

- Do not use `relates_to` as if it meant "blocks". An undirected edge cannot carry an
  order, and an agent reading it later will invent one.
- Do not quietly fall back to prose ordering in the index either; `SKILL.md` is right
  that prose which could have been an edge drifts.
- Say plainly that the instance cannot hold the graph, and propose a convention to the
  user: for example, a fixed first line in the dependent issue's **description** (not a
  note, so it stays current and searchable), `Blocked by: #17`, written as
  `group/project#17` whenever the blocker is in another project, plus a `relates_to`
  link so the two issues still find each other.
  It is queryable with a text search, which is weaker than a native edge and stronger
  than a sentence in the index. Record the convention in the stanza, and tag it
  `derived` until the user adopts it.

Encode only edges that carry information, exactly as in `SKILL.md`, whichever
mechanism you end up with.

## Refinement and research issues

- **Distinguish them by label.** GitLab issue types are fixed (`issue`, `incident`,
  `test_case`, plus tasks), so the refinement/research/feature distinction is a label.
  Use the project's scheme; if it has scoped labels and is on Premium+, a
  `kind::refinement` / `kind::research` / `kind::feature` axis is exclusive for free.
  Creating that axis is a label-set change: propose it, do not just apply it (see
  `github-issues:triaging-issues`). And beware that `--label` with a name that does
  not exist **creates** the label.
- **Tasks are not features.** GitLab child tasks under an issue are a good home for a
  feature's own implementation steps once it is ready. Using tasks under a refinement
  issue to sketch features is creating feature issues by another name, before
  refinement; the stop rules still apply.
- **Templates.** GitLab templates are plain Markdown in `.gitlab/issue_templates/`,
  may be inherited from the group or instance, and are not enforced on any path. List
  them with `glab api "projects/:fullpath/templates/issues"` before deciding there is
  none.
- **The research verdict** goes in the closing comment, as in `SKILL.md`. GitLab has no
  close reason, so the comment is the only place the outcome is recorded; a research
  issue closed without one has lost its output.

## Completeness reads the same way

A GitLab milestone, like a GitHub one, reports progress as closed issues over total
issues and shows 100% when its list empties. An epic reports progress over its
children. Neither knows the acceptance criterion. Everything `SKILL.md` says about "an
empty issue list is not delivery" holds here unchanged.

## Linking

Use GitLab's reference sigils so links are real: `#N` issue, `!N` merge request,
`%"title"` milestone, `&N` epic, `group/project#N` across projects. The index links to
each milestone or epic by URL; each milestone or epic description links back to the
index path, as in `SKILL.md`.
