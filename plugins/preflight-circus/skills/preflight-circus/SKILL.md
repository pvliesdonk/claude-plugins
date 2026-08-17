---
name: preflight-circus
description: Keeps AI-induced technical debt out of the repository. Use before every push that creates or updates a PR — `gh pr create` on a fresh branch, `gh pr ready <N>` flipping a draft, or any `git push` to a branch with an open PR (responding to a bot finding, a human review comment, or adding further work). Runs the six-lens blind gate over `BASE..HEAD` via the circus.workflow.js Workflow — the same examination a post-push review bot applies, sat before the push instead of after it.
---

# Preflight Circus

The gate a change passes before its push. It exists to keep AI-induced
technical debt out of the repository — that is what is at stake in every
paragraph below, and it is what the strictness of `structural` and of the
terminal two-round cap are for.

A post-push review bot — typically a GitHub Actions workflow invoking
`/code-review:code-review` once the PR is open — examines the change after it
reaches the remote; this skill applies that same examination beforehand,
against a local `BASE..HEAD` range instead of a PR URL.

`circus.workflow.js`'s file header names the canonical upstream prompt and
says which side wins on drift. That note sits next to the prompts it governs,
so this skill does not restate it.

## When to run

Run before **every push that creates or updates a PR** — all three trigger
points produce a cumulative diff the post-push bot will re-review, so all
three must be cleared locally first:

- Before `gh pr create` on a fresh branch.
- Before `gh pr ready <N>` flipping a draft PR to ready.
- Before any `git push` that updates an open PR — whether responding to a bot
  finding, a human review comment, or adding further work to the same branch.

Do not skip for "small" diffs, "docs-only" diffs, "just fixing the typo the
bot found", or "obviously OK" diffs. Whatever PR policy your `CLAUDE.md` tree
sets is what makes the invocation mandatory; this skill is only the mechanic.

### The circus confirms; it does not discover

The circus is an exam, not a linter. You prepare, then you sit it; it does not
teach you. A single run costs roughly forty agents, so the work it checks is
work done beforehand — informally, in your head, over your own diff — and you
invoke expecting to pass. A clean first run is the ordinary outcome, and it is
what preparation looks like.

**You can know the pass condition in advance, and you already hold everything
needed to meet it.** The lenses have no access you lack: they read the
`CLAUDE.md` tree, the git history, prior PR comments, the code's own comments,
and the diff hunks. Every one of those is open to you, the context is already
loaded, and you pay no dispatch or worktree setup cost. Your access is
strictly better than theirs, not merely equivalent.

**The bar is not the circus's own — it is yours, and it is applied without
mercy.** The gate invents no standard. It holds the change to what has already
been committed to in writing: the rules in the `CLAUDE.md` tree, decisions
settled in earlier PR reviews, what the code's own comments and docstrings
promise, the intent recorded in git history, and whatever conformance a spec
requires. Where it is not the project's declared rule, it is the floor any
working code meets — a plain bug clears no bar anywhere. That is why the pass
condition is knowable in advance: the syllabus is written down, and it was open
to you before you sat. What the circus adds is not a higher bar but an
unforgiving application of the existing one, with no room to negotiate.

So anything the circus can find, you can find first, sooner and cheaper. A
finding is never news about the diff; it is something the preparation would
have caught.

## Procedure

### 1. Compute the range

    DEFAULT=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)
    git fetch origin "$DEFAULT"
    BASE=$(git merge-base HEAD "origin/$DEFAULT")
    HEAD=$(git rev-parse HEAD)
    REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
    MODIFIED=$(git diff --name-only "$BASE".."$HEAD")
    printf 'BASE=%s\nHEAD=%s\nREPO=%s\nMODIFIED:\n%s\n' \
      "$BASE" "$HEAD" "$REPO" "$MODIFIED"

Derive the default branch rather than hardcoding `main`: a repo whose default
is `master` or `develop` but which still carries a stale `origin/main` would
otherwise resolve an ancient merge-base and examine hundreds of unrelated files.

The range is always `BASE..HEAD` against the merge-base with the default
branch — never "last push..HEAD". The post-push bot re-reviews the whole
cumulative diff on every push, so the circus must too.

**Read the printed values.** They are the input to step 2, and you paste them
in as literal strings — the Workflow tool runs in its own process and cannot
see this shell's variables.

### 2. Run the circus

Substitute the four printed values for the `<...>` placeholders below. They
are literal strings in the `args` object, not shell variables and not names
the script resolves.

    Workflow({
      scriptPath: "${CLAUDE_PLUGIN_ROOT}/workflows/circus.workflow.js",
      args: {
        base: "<the BASE hex SHA printed above>",
        head: "<the HEAD hex SHA printed above>",
        repo: "<owner/name printed above>",
        modified: "<the newline-separated MODIFIED paths printed above>"
      }
    })

The script validates the shape of all four before dispatching anything, so a
placeholder pasted through unsubstituted aborts loudly instead of examining an
empty range and reporting it clean.

The script owns the lens set, the prompts, the dispatch, the scoring, the
threshold, and the verdict it derives from them. There is nothing to configure
and no subset to request.

### 3. Act on the result

    { status, verdict, lensesRun, lensesSkipped, coreErrors, degraded,
      rawCounts, surviving, unscored }

`verdict: { name, directive }` is the permission slip. `status` describes what
happened; the verdict states what you may do next, and the `directive` string
carries that instruction in full. Read it before the findings.

- `blocked` — you may not triage. The run did not complete, so the findings
  list is not evidence of anything either way. Fix the invocation or the
  environment and run it again.
- `clear` — you may push.
- `fix-and-rerun` — you may fix each surviving finding, or defend it, and then
  you must re-run the whole circus. You may not push on this verdict.
- `structural` — you may **not** fix these and re-run. That is forbidden here,
  not discouraged: a list this long is itself the finding rather than a
  workload. Stop, diagnose why it is long, and expect to restart from a clean
  state.

The verdict is count-based and round-agnostic, because the script is stateless
and cannot know which round this is. `structural` is therefore stricter than
the two-round cap below rather than in tension with it: the cap is a ceiling,
and `structural` can stop you at round one. It is also indifferent to
`degraded` — a lens reporting `partial` never blocks `clear`.

- `status: 'error'` — a core lens did not run (see `coreErrors`), a finding
  lost its score to a dead scoring agent (a non-empty `unscored`), or a core
  lens reported it could not examine the range at all (a `degraded` entry
  with `core: true` and `examined: 'none'`).
  None is a clean result and none is a finding to triage — diagnose it
  before pushing anything. A `coreErrors` entry with `id: 'args'` means the
  step-1 values did not reach the script in the expected shape; it names the
  offending key. Redo step 1 and re-paste; do not hand-edit the args.
  Each `unscored` entry carries the finding's
  fields — including `lens`, naming which lens surfaced it — plus
  `score: null`, `justification: null`, and a `reason`: a lens surfaced it,
  but its scorer died before saying whether it clears the bar.
- `degraded` — lenses that ran but could not see the whole range, each with
  its `examined` level and the `blockers` that stopped it. `examined:
  'partial'` is informational and never gates: the lens still reached a real
  conclusion, and a permanently missing optional tool must not error every
  run. Read the blockers anyway — they name a capability worth installing,
  and a lens that has been `partial` for weeks is reviewing at half strength.
  `examined: 'none'` on a core lens is the one that gates, and is why
  `status` is `error`; on a supplementary agent it is a logged `skipped`
  entry instead.
- `status: 'clean'` — nothing cleared the threshold. Push.
- `status: 'findings'` — for each entry in `surviving`, either fix the
  underlying issue, or write a one-line defense naming the entry's `lens`
  to recalibrate and treat it as resolved. Do not silently skip.

**On `verdict: 'structural'`, stop and diagnose, before you fix anything.**
Where that line falls is the script's to set and not this skill's to restate.
A long list is not a workload to get through; it is the signal that something
is very wrong. The count is a diagnostic, never a budget or an allowance — "I
am still under the line" is no more a clearance than "I have used my two
rounds" is. Patching your way down a long list is the linter behavior this
skill forbids: each fix makes the next round cheaper to rationalize, and you
arrive at the cap having never asked why the list was long. None of this says
invoke rarely, or only when certain of zero findings — the gate still has to
run. It says a first run should come back clean or near-clean, and when it
does not, the length of the list is the thing to explain.

**Use the pull to work around a finding as a signal.** It is free information:
the pull to explain a finding away is not evidence that the finding is wrong,
it is the most reliable tell that it is right. Notice it, and read the finding
again before you write a word of defense.

**When a defense is not accepted, the claim is too large — not the evidence
too thin.** If the user does not accept a defense, or asks for more evidence,
the instinct is to marshal more evidence, and that instinct feels like
integrity while usually being the opposite. The correct inference is that the
claim exceeds what you can back up. Do not fortify it. Narrow it. Then ask
whether the claim is load-bearing at all — a disputed claim that is holding
nothing up gets dropped entirely, not defended in a smaller form. A defense is
honest only when it is smaller than the finding, never louder.

Then go back to step 1. The range moves when you commit a fix.

## Two rounds, then stop

If a second local round still returns findings, stop and surface it to the
user with an explanation. Do not start a third round.

The cap is a circuit-breaker for a broken design, not permission to ship
unclean. Reaching it never authorizes a push: "I have used my two rounds" is
not a clearance.

Reaching the cap is also not a stage you pass through on the way to a third
attempt. There may be no further attempt: the change can be handed to a fresh
attempt starting from a clean state, or abandoned. Do not plan around a third
round existing, and do not write the escalation as a request for permission to
continue. That is what the cap costs, and it is why the preparation belongs
before the first invocation rather than after the second.

Every second-round failure observed so far comes out the same way: the
preparation did not happen. The pass condition was knowable in advance and the
access was there, so a second round is arithmetic rather than bad luck — you
did not pass, so you had not prepared. Start the diagnosis there, not at the
diff and not at the lenses.

So answer it first, in writing: what did you do on the diff before the first
invocation? If you cannot describe that self-review concretely, it is the
diagnosis and you are done looking.

The script is stateless by design — that is what makes "I only re-ran lens 1"
impossible — so it cannot notice that round two surfaced the same class as
round one. Only this skill sits across rounds, so only this skill can see the
pattern that says stop.

The other two explanations are earned, not offered, and each needs evidence
you almost certainly do not have:

- **The findings share one root cause.** Only if you can name the cause.
  Feeling related is not sharing a root cause. When you can name it, the
  design is wrong rather than the implementation that exposed it: treat the
  branch as a spike, return to the design, and restart from a clean state
  rather than patching.
- **A lens is mis-calibrated.** The least likely and the most self-serving.
  It asserts a defect in a system that has been reviewed and calibrated, on
  the evidence of your own two failed rounds and nothing else. That is the
  over-claiming error the defense rule above names, aimed at the tool instead
  of at a finding. Narrow it or drop it.

Lead the escalation with the preparation assessment: what was not done before
invoking, and only then the findings. Buried, it stops being an assessment and
becomes a findings report; padded with self-justification, so does it. State
it plainly and leave it there.

The same cap already applies after a PR opens: if a bot finds something on a
second post-push round, surface it rather than pushing a third time.

## Re-running after a bot finding

If a bot post-push catches something the local circus missed:

1. Apply the fix.
2. Re-run the circus (step 2 of the Procedure) against the new `BASE..HEAD`.
3. If a bot finds something on a second post-push round, surface it to the
   user rather than pushing a third time — see "Two rounds, then stop" above.
