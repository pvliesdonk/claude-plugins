---
name: triaging-issues
description: Use when sorting or cleaning up a GitHub or GitLab issue backlog (gitlab.com or self-managed), deciding an issue's labels, priority or milestone, setting up labels in a repo that has none or only GitHub's defaults, or curating a label set that has grown duplicates and dead entries.
---

# Triaging Issues

## The Rule: Classify Within the Scheme, Don't Redesign It

Triage answers four questions about an issue: **what kind, whose area, how urgent, and when.** That is all.

**STOP. Before you touch anything:**
> Am I about to redesign the label set, or diagnose the bug?

Both mean you have stopped triaging. Redesigning the taxonomy is a separate task with its own risks (below). Diagnosing belongs to whoever picks the issue up.

Companion skill: `github-issues:writing-issues` covers how to *write* an issue — reach for it when the issue does not exist yet. This one is for issues that already do.

**This skill assumes nothing about the repo.** It is written to work where there are no
conventions yet and where they differ from anything described here. Where the project
states a rule — `CONTRIBUTING.md`, an issue form, a documented scheme — **that rule wins
and this skill is the fallback**; where it states nothing, everything here applies as
written. Say which of the two you are in before you start.

## Step 0: Which Forge

The disciplines below hold on both GitHub and GitLab. The commands, and several of the
traps, do not. Read the remote before anything else:

```bash
git remote get-url origin
```

- `github.com` (or a GitHub Enterprise host) — the `gh` commands in this file and
  [mechanics.md](mechanics.md) apply.
- Otherwise, a host that answers `glab api version` is **GitLab**, hosted or
  self-managed. (A GitHub Enterprise host fails this probe, which is why the GitHub
  check comes first.)
  Read [mechanics-gitlab.md](mechanics-gitlab.md) Step 0 first: on GitLab the
  instance **version and licence tier** decide whether scoped labels are exclusive,
  whether issues can block each other, and whether labels can be archived. State the
  host, version and tier you found before proposing anything.

- Neither (Gitea, Forgejo, Bitbucket, …) — stop and say so. The disciplines still
  apply, but there are no verified mechanics for that forge; do not improvise commands.

Where this file shows a `gh` command, mechanics-gitlab.md has the GitLab equivalent.
Vocabulary: a GitHub pull request is a GitLab merge request (`!N`), and GitLab has no
close reason (below).

## Step 1: Read the Taxonomy Before You Label Anything

Never label from memory or from a taxonomy someone pasted at you. Read the live one:

```bash
gh label list --limit 200                    # NOT bare — see the trap below
ls .github/ISSUE_TEMPLATE/*.yml              # forms define the canonical type vocabulary
grep -h 'labels:' .github/ISSUE_TEMPLATE/*.yml
gh api repos/:owner/:repo/milestones --jq '.[]|"\(.number) \(.title) open=\(.open_issues)"'
```

**The truncation trap:** `gh label list` and `gh issue list` both default to `--limit 30`, and labels sort by *creation date* — so the bare command hides the newest labels, which are the ones triage needs. Measured on a real 37-label repo, the default listing hid `feature`, `epic`, `decay`, `priority:medium` and `ships-atomically` while leaving `enhancement` visible: you "discover" that `feature` doesn't exist, reach for the legacy twin, and deepen the split you were asked to fix. **Always pass `--limit`.**

**Labels an issue form applies are the canonical vocabulary.** If `feature-request.yml` emits `feature`, then `feature` wins and `enhancement` is legacy — regardless of which has more issues on it. On GitLab the equivalent is a `/label ~feature` quick action inside a `.gitlab/issue_templates/*.md` file — and templates can be inherited from the group or instance, so they may not be in the repository at all. List them through the API (mechanics-gitlab.md), not with `ls`.

**On GitLab, labels may belong to the group, not the project.** A group label is shared by every project under it. Read which kind each label is before you count, rename or retire anything.

Also read `CONTRIBUTING.md` / `CLAUDE.md` for local rules. Milestone semantics in particular are project-specific and often load-bearing.

## Step 2: Read the Issue, Not the Title

Open the body before assigning anything beyond an obvious type label. A descriptive title tells you the *kind*; it does not tell you severity, whether it is still live, or whether it duplicates something.

If you are triaging in bulk and will not read 40 bodies, say so and triage only the dimension titles genuinely support. **Do not emit confident priorities derived from titles.** Mark what you did not read.

## The Contract: What a Triaged Issue Carries

Every triaged issue carries exactly:

- **one** type label — `bug` / `feature` / `docs` / `chore` / `question` / whatever the forms emit
- **zero or more** area labels — component, subsystem, surface
- **one** priority label, **or none deliberately**
- **zero or more** status labels — `blocked`, `needs-info`, `duplicate`

Four axes, and that is the whole output. Two type labels on one issue is the most common triage defect: an issue is not both a bug and a question. Pick the one that decides what happens next.

GitLab scoped labels (`priority::high`) enforce "one per axis" natively, but only on Premium and Ultimate — and they enforce it by **silently removing** the sibling. So on those tiers, adding a scoped priority label *is* a priority change, whatever the command looks like. On Free, scoped names carry no exclusivity and the contract is yours to keep.

If you find yourself adding a fifth kind of thing, you are inventing taxonomy — stop and see Curating below.

## Milestones: Read What They Mean Here First

Labels say **what an issue is** (many per issue). A milestone says something about *when* — but **what exactly varies by project**, and guessing is destructive in both directions. Establish the scheme before you touch one:

| Scheme | A milestone is | Tell |
|---|---|---|
| Release payload | the work committed to a named release | titled like a version (`v4.1`); often "safe to cut" = no open issues in it |
| Epic / idea | a body of intent being refined into features | titled like a theme; carries an acceptance criterion and a refinement issue |
| Timebox (GitLab, common) | a sprint or a period | has start and due dates; on Premium, iterations usually do this job instead |

On GitLab, milestones exist at both project and group level, and an issue can sit in a group milestone shared with other projects. A group milestone is somebody else's commitment as well as this project's; changing one is never a local edit.

`CONTRIBUTING.md`, `CLAUDE.md`, and the existing milestone titles tell you which. **Where milestones are epics, never strip one as speculative** — an unshipped milestone there is the roadmap, not a wishlist entry, and the rest of this section does not apply to it.

Everything below is the **release-payload** scheme. Under it, assign a milestone only when **both** hold:
1. You can name the release it ships in, and
2. the work is actually committed to that release.

If you cannot name the release, leave it off. **Absence of a milestone is the backlog** — that is what the backlog is, under this scheme. A milestone holding every open issue is a wish list, and it destroys the only question milestones answer.

Many projects gate releases on milestone emptiness ("safe to cut = no open issues in the milestone"). Where that is true, **adding a milestone blocks a release** — always confirm it. Check `CONTRIBUTING.md` before assuming it isn't true here.

Do not create a `Backlog` milestone. It shows up in the same queries and re-poisons the signal that milestone-emptiness carries.

## Closing Is a Triage Outcome

Close on a **reason**, never on age. Staleness is a signal to look, not a verdict — auto-closing on inactivity discards exactly the issues nobody had bandwidth for.

| Reason | How |
|---|---|
| Duplicate | `--reason duplicate --duplicate-of N` — link, don't just close |
| Already fixed | `--reason completed`, citing the PR or symbol that fixed it |
| Won't fix | `--reason "not planned"` + a sentence of why |
| Cannot reproduce | Ask first; close only after the ask goes unanswered |

GitLab has **no close reason field**. The reason exists only in the closing comment, so the comment is mandatory. Duplicates use the `/duplicate #N` quick action, which closes and links in one step; everything else is a comment naming the reason, then a close.

**Fixed-but-unreleased is not "fixed" to the reporter.** If the fix is on the main branch but not in a release, say that explicitly — closing with a bare "already fixed" reads as dismissal to someone running the released version.

**Bot artifacts are not issues.** Renovate's Dependency Dashboard, automated sync trackers — exclude them from triage sweeps rather than labelling them.

## What to Apply vs What to Confirm

**Apply directly** — this list is closed. Nothing joins it by analogy:
- adding a type or area label the issue plainly states
- removing a label that is verifiably wrong
- swapping a legacy duplicate label for its canonical twin

Three operations, and the list is exhaustive. Note what is *not* on it: the list covers **label operations only**. Editing an issue's title or body, closing it, assigning it, or inferring a type from evidence outside the issue are all decisions, not clerical fixes — they belong below.

**Propose, then wait for a decision:**
- priority — it encodes *someone else's* urgency, not yours
- any milestone change, and anything the repo documents as release-gating
- any close, retitle, or edit to issue content
- any label create / rename / delete
- any type label you inferred rather than read

Present proposals as a table (issue → change → one-line reason), grouped so the gating and destructive rows are not buried among trivial ones.

## A Repo With No Labels

A new repo is not empty — GitHub seeds exactly nine defaults: `bug`, `documentation`, `duplicate`, `enhancement`, `good first issue`, `help wanted`, `invalid`, `question`, `wontfix`. Several are already obsolete: `duplicate`, `invalid` and `wontfix` duplicate the native `state_reason` values.

**Do not scaffold thirty labels into an empty repo.** A label earns its place by answering a question someone actually asks. Start with the type axis only, pick `enhancement` *or* `feature` and never both, and add an area label the first time you genuinely cannot find something without it. Prefix an axis only when it has enough members to need grouping (`area:`, `priority:`); bare names are fine for types and read better in the UI.

A new GitLab project seeds **no** labels, but it may inherit a full set from its group. Before calling a GitLab project empty, list labels including ancestor groups; if the group already has a type axis, use it rather than shadowing it with project labels of the same name.

Conventions differ per repo — match the one you are in rather than importing a scheme from elsewhere.

## Curating an Existing Taxonomy

This is the destructive part. Separate it from a triage sweep; do not bundle them.

- **Rename, don't delete-and-recreate.** `gh label edit <old> --name <new>` preserves every existing assignment. Delete-then-create loses them all.
- **Deleting a label strips it from closed issues too**, destroying historical attribution. Count the blast radius across `--state all` before deleting anything.
- **Retire in place instead of deleting.** A dead label costs nothing but picker noise, and that is fixable without losing history: grey it out and say so in the description — `gh label edit future --color cccccc --description "RETIRED — no milestone is the backlog"`. Deletion buys a shorter picker at the price of history. GitLab 18.11+ can **archive** a label natively, which is exactly this.
- **On GitLab, a group label's blast radius is the whole group.** Count across every project that inherits it, and treat renaming one as a change to all of them. Never promote a project label to a group label during curation: it is irreversible and merges same-named labels in sibling projects.
- **On GitLab, a typo in a label you apply creates a new label.** That is curation by accident. Match every name against the live list first.
- **The one case where deleting is free** is a repo with no history to lose — a new repo whose unwanted defaults have never been applied. Prove it rather than assume it: the blast-radius count across `--state all` must be zero for issues *and* PRs.
- **Merge only true synonyms.** `enhancement` → `feature` is a merge. `performance` → `bug` and `refactor` → `decay` are not — they discard a distinction someone made.
- **Migrate issues before deleting the losing label**, then verify it is unused.
- **Never rename a bot-owned or form-owned label** without changing the config that emits it (`renovate.json`, `.github/ISSUE_TEMPLATE/*.yml`, workflows; on GitLab `.triage-policies.yml`, `/label` lines in `.gitlab/issue_templates/`, CI jobs). The bot will recreate it, and now you have both. GitLab issue board lists are bound to labels too: deleting one removes the board column.

## Rationalization Table

| Excuse | Reality |
|---|---|
| "The taxonomy is a mess, I should fix it first" | Triage and curation are different tasks with different risk. Do the sweep within the scheme that exists; propose curation separately. |
| "The titles are descriptive enough" | Titles give you type. They do not give you severity, liveness, or duplicates. |
| "It's obviously low priority" | Priority is the maintainer's call about their own time. Propose it. |
| "A milestone will help organise the backlog" | That is what labels are for. Under the release-payload scheme a milestone is a shipping commitment, often a release gate. |
| "This milestone has no release date, so it is speculative" | Or the project uses milestones as epics. Establish the scheme before stripping anything. |
| "This issue is ancient, close it" | Age is not a reason. Find a reason or leave it open. |
| "I'll just add both labels to be safe" | Two type labels means the axis no longer answers anything. Pick one. |
| "The label list I was given is the taxonomy" | Re-read it live with `--limit 200`. Pasted lists and truncated ones are how duplicate labels get created. |
| "Deleting the unused label is tidy" | It strips the label off closed issues and destroys history. Retire it in place. |
| "While I'm in here I'll fix the title too" | The title is the reporter's words. Retitling is a proposal, not a clerical fix. |
| "This one's cheap, it belongs in apply-directly" | That list is closed at three items. If you are arguing for an addition, it is a proposal. |

## Red Flags — Stop

- Proposing new labels during a triage sweep
- Any `gh label delete` you have not counted `--state all` for
- A priority or milestone on an issue whose body you did not open
- `bug` and `question` (or any two types) on the same issue
- A closing comment that does not name a reason
- A bare `gh label list` or `gh issue list` in your triage transcript — or a bare `glab label list` / `glab issue list`, which truncate at 30 the same way
- On GitLab: a label name you did not match against the live list, or a group label edited from a project-level task
- A milestone added or removed before you established what milestones mean in this repo
- Anything in your apply-directly block that is not one of the three listed operations

## Mechanics

Exact commands for all three tool paths — `gh` CLI, `gh api`, and the GitHub MCP server, including which operations each path cannot do and the label-replacement trap in the API/MCP path — are in [mechanics.md](mechanics.md).

The GitLab equivalents — `glab`, `glab api`, and GitLab's MCP server, with instance version and tier detection for self-managed hosts — are in [mechanics-gitlab.md](mechanics-gitlab.md).
