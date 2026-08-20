---
name: triaging-issues
description: Use when sorting or cleaning up a GitHub issue backlog, deciding an issue's labels, priority or milestone, setting up labels in a repo that has none or only GitHub's defaults, or curating a label set that has grown duplicates and dead entries.
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

## Step 1: Read the Taxonomy Before You Label Anything

Never label from memory or from a taxonomy someone pasted at you. Read the live one:

```bash
gh label list --limit 200                    # NOT bare — see the trap below
ls .github/ISSUE_TEMPLATE/*.yml              # forms define the canonical type vocabulary
grep -h 'labels:' .github/ISSUE_TEMPLATE/*.yml
gh api repos/:owner/:repo/milestones --jq '.[]|"\(.number) \(.title) open=\(.open_issues)"'
```

**The truncation trap:** `gh label list` and `gh issue list` both default to `--limit 30`, and labels sort by *creation date* — so the bare command hides the newest labels, which are the ones triage needs. Measured on a real 37-label repo, the default listing hid `feature`, `epic`, `decay`, `priority:medium` and `ships-atomically` while leaving `enhancement` visible: you "discover" that `feature` doesn't exist, reach for the legacy twin, and deepen the split you were asked to fix. **Always pass `--limit`.**

**Labels an issue form applies are the canonical vocabulary.** If `feature-request.yml` emits `feature`, then `feature` wins and `enhancement` is legacy — regardless of which has more issues on it.

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

If you find yourself adding a fifth kind of thing, you are inventing taxonomy — stop and see Curating below.

## Milestones: Read What They Mean Here First

Labels say **what an issue is** (many per issue). A milestone says something about *when* — but **what exactly varies by project**, and guessing is destructive in both directions. Establish the scheme before you touch one:

| Scheme | A milestone is | Tell |
|---|---|---|
| Release payload | the work committed to a named release | titled like a version (`v4.1`); often "safe to cut" = no open issues in it |
| Epic / idea | a body of intent being refined into features | titled like a theme; carries an acceptance criterion and a refinement issue |

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

Conventions differ per repo — match the one you are in rather than importing a scheme from elsewhere.

## Curating an Existing Taxonomy

This is the destructive part. Separate it from a triage sweep; do not bundle them.

- **Rename, don't delete-and-recreate.** `gh label edit <old> --name <new>` preserves every existing assignment. Delete-then-create loses them all.
- **Deleting a label strips it from closed issues too**, destroying historical attribution. Count the blast radius across `--state all` before deleting anything.
- **Retire in place instead of deleting.** A dead label costs nothing but picker noise, and that is fixable without losing history: grey it out and say so in the description — `gh label edit future --color cccccc --description "RETIRED — no milestone is the backlog"`. Deletion buys a shorter picker at the price of history.
- **The one case where deleting is free** is a repo with no history to lose — a new repo whose unwanted defaults have never been applied. Prove it rather than assume it: the blast-radius count across `--state all` must be zero for issues *and* PRs.
- **Merge only true synonyms.** `enhancement` → `feature` is a merge. `performance` → `bug` and `refactor` → `decay` are not — they discard a distinction someone made.
- **Migrate issues before deleting the losing label**, then verify it is unused.
- **Never rename a bot-owned or form-owned label** without changing the config that emits it (`renovate.json`, `.github/ISSUE_TEMPLATE/*.yml`, workflows). The bot will recreate it, and now you have both.

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
- A bare `gh label list` or `gh issue list` in your triage transcript
- A milestone added or removed before you established what milestones mean in this repo
- Anything in your apply-directly block that is not one of the three listed operations

## Mechanics

Exact commands for all three tool paths — `gh` CLI, `gh api`, and the GitHub MCP server, including which operations each path cannot do and the label-replacement trap in the API/MCP path — are in [mechanics.md](mechanics.md).
