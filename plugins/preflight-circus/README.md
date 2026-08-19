# preflight-circus

A blind, multi-lens review gate over `BASE..HEAD`, sat **before** you push
rather than after. It exists to keep AI-induced technical debt out of the
repository.

Most projects already run some post-push review bot on an opened PR. By then
the diff is public, the branch is pushed, and every finding costs a round
trip. This plugin applies the same examination while the change is still
local.

## Install

```
/plugin marketplace add pvliesdonk/claude-plugins
/plugin install preflight-circus
```

## What it runs

Six core lenses, dispatched in parallel and **blind to one another**, each
reading the diff plus a different body of prior commitment:

| Lens | Holds the change against |
| --- | --- |
| `lens-1-claude-md` | every `CLAUDE.md` applicable to the changed files |
| `lens-2-shallow-diff` | the diff hunks on their own terms |
| `lens-3-git-history` | the intent recorded in the history it lands on |
| `lens-4-past-prs` | decisions already settled in earlier PR reviews |
| `lens-5-code-comments` | what the code's own comments and docstrings promise |
| `lens-6-normative-conformance` | whatever conformance a spec requires |

If the [`pr-review-toolkit`](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/pr-review-toolkit)
plugin is installed, its five agents join as supplementary lenses. It is not a
dependency — they are skipped, and logged as skipped, when absent.

Every finding is then scored for confidence by a separate pass, and anything
below the threshold is dropped before you ever see it. A run costs roughly
forty agents.

## What comes back

```js
{ status, verdict, lensesRun, lensesSkipped, coreErrors, degraded,
  rawCounts, surviving, unscored }
```

`verdict` is the permission slip, and it is count-based:

| Surviving findings | Verdict | What you may do |
| --- | --- | --- |
| — (run failed) | `blocked` | Nothing. The findings list is not evidence either way; fix the environment and re-run. |
| 0 | `clear` | Push. |
| 1–3 | `fix-and-rerun` | Fix or defend each one, then re-run the whole gate. |
| 4+ | `structural` | **Stop.** Fixing these and re-running is refused, not discouraged. |

`structural` is the part people delete first and regret. A long list is not a
workload to grind through — it is the finding. Patching down the list is
exactly the linter behaviour this gate exists to refuse, and each fix makes
the next round cheaper to rationalise.

## Design notes

**It confirms; it does not discover.** The gate is an exam, not a linter. The
lenses have no access you lack — they read the same `CLAUDE.md` tree, history,
PR comments and hunks that are already open to you, and you pay no dispatch
cost. So the pass condition is knowable in advance, and a clean first run is
the ordinary outcome. A finding is never news about the diff; it is something
the preparation would have caught.

**The bar is yours, not the gate's.** It invents no standard. It holds the
change to what has already been committed to in writing, plus the floor any
working code meets. What it adds is an unforgiving application of the existing
bar, with no room to negotiate.

**Two rounds, then stop.** If a second local round still returns findings, the
skill escalates rather than starting a third. The cap is a circuit-breaker for
a broken design, and reaching it never authorises a push.

**The script is stateless.** It cannot know which round this is, which is what
makes "I only re-ran lens 1" impossible.

## Layout

```
preflight-circus/
├── skills/preflight-circus/SKILL.md   # when to run it, how to read the result
└── workflows/circus.workflow.js       # the lenses, prompts, dispatch and scoring
```

The skill is the operator; the workflow owns the lens set, the prompts, the
threshold and the verdict. There is nothing to configure and no subset to
request.

## Licence

MIT — see the [repository LICENSE](../../LICENSE).
