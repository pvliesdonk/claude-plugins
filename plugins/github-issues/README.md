# github-issues

Two disciplines for GitHub issues, one for each half of an issue's life:
writing one that does not yet exist, and classifying the ones that already do.

Both exist for the same reason. An agent handed an issue will reach past what
it observed — asserting a cause it never verified, a priority it inferred from
a title, a release commitment nobody made. The failure is invisible in the
output: an unverified claim reads exactly like a verified one, and whoever
picks the issue up inherits a false floor of confidence.

## Install

```
/plugin marketplace add pvliesdonk/claude-plugins
/plugin install github-issues
```

## The two skills

| Skill | Use when | Refuses to |
| --- | --- | --- |
| `writing-issues` | the issue does not exist yet — a bug to file, a finding from review, a ticket to draft | assert a cause, propose a fix, or bundle a second problem into one body |
| `triaging-issues` | the issue exists — labels, priority, milestone, a backlog sweep, or a label set gone to seed | derive priorities from titles, redesign the taxonomy mid-sweep, or delete a label without counting what it strips |

They are deliberately separate. Writing is about a body you are composing;
triage is about a scheme you are classifying into. The one place they meet is
`.github/ISSUE_TEMPLATE/` — and even there they read it for different things:
writing wants the form's fields, triage wants its label vocabulary.

## writing-issues

The rule is **observation, not work order.** The body records what was seen;
it does not diagnose, design, or prescribe. Every cause statement carries
`[verified: how]` or `[unverified]`, and an unverified cause requires the
sentence "I have not verified the cause" — so the reader inherits the doubt
rather than a confident-sounding guess.

Also enforces one issue per observed problem, and fills the repo's own issue
form when one exists rather than inventing fields.

## triaging-issues

The rule is **classify within the scheme, don't redesign it.** Triage answers
four questions — what kind, whose area, how urgent, and when — and a
triaged issue carries exactly one type label, zero or more area labels, one
priority or none deliberately, and zero or more status labels.

Load-bearing distinctions it holds:

- **Establish what a milestone means here before touching one.** Under the
  release-payload convention it is a shipping commitment, often gating "safe to
  cut a release", and absence of one is the backlog. Under the epic convention
  (`roadmapping`) it is a body of intent being refined, and stripping it as
  speculative destroys the roadmap. The skill names both and refuses to guess.
- **Close on a reason, never on age.** Staleness is a signal to look.
- **Renaming preserves assignments; deleting strips the label off closed
  issues too.** Retire in place instead.
- **Bot- and form-owned labels have an emitter.** Rename one without changing
  its config and you end up with both.

Work splits into what an agent may apply directly (three label operations,
exhaustively listed) and what it must propose and wait on (priority,
milestones, closes, and any change to the label set itself).

`skills/triaging-issues/mechanics.md` carries verified commands for all three
tool paths — `gh`, `gh api`, and the GitHub MCP server — with a capability
matrix, because none of the three can do everything:

- there is no `gh milestone` command at all; milestones need `gh api`
- `gh label list` and `gh issue list` both default to `--limit 30`, and labels
  sort by creation date, so the bare command hides the newest labels
- in the API and MCP paths, `labels` **replaces** the whole set rather than
  appending, and `milestone` takes a number where `gh` takes a title

## Tests

Each skill ships its pressure scenarios under `tests/`, with the baseline
behaviour they were written against. Run one against a fresh subagent, once
without the skill and once with it, and sandbox the agent — tell it `gh` is
unauthenticated and the deliverable is the commands it *would* run — so a test
can never mutate a real repository.
