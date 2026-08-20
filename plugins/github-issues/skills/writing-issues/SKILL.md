---
name: writing-issues
description: Use when filing a bug, opening or creating a GitHub issue, drafting a ticket, writing up a finding or observation as an issue, when a code review or brainstorm surfaces a problem worth tracking, or when writing the description for a pull request you are about to open.
---

# Writing Issues

Two documents, written at opposite ends of the work: the **issue** that opens it and the
**pull request description** that closes it. Both are read by someone without your
context — a reviewer now, or someone reconstructing intent years later — and both
fail the same way: claiming more confidence than you earned, and omitting what you
left out.

Steps 1–2 cover issues; **Pull Request Descriptions** covers the other half. Everything
else here — the uncertainty rule, the scope rule, and the clause below about deferring
to the repo's own conventions — governs both.

## The Rule: Observation, Not Work Order

You are recording what was observed. You are not diagnosing, designing, or prescribing.

**STOP. Before writing a single word:**
> Am I about to describe how to fix this, propose an architecture, or assert a root cause?

If yes — **remove it.** The issue body must contain no proposed approach and no asserted cause. An issue that reads like a work order misleads implementers into treating your imagination as researched fact.

Companion skill: `github-issues:triaging-issues` covers what to do with an issue that already exists — labels, priority, milestone, closing. Filing is this skill; classifying is that one. Do not label or milestone as part of filing beyond what the issue form applies.

**This skill assumes nothing about the repo.** It is written to work where there are no
conventions yet and where they differ from anything described here. Where the project
states a rule — `CONTRIBUTING.md`, an issue form, a documented scheme — **that rule wins
and this skill is the fallback**; where it states nothing, everything here applies as
written. Say which of the two you are in before you start.

## Step 1: Check for a Template (Always Do This First)

```bash
ls .github/ISSUE_TEMPLATE/        # directory form (.md or .yml files)
cat .github/ISSUE_TEMPLATE.md     # legacy single file
cat .github/ISSUE_TEMPLATE/config.yml  # chooser
```

**Template found:**
- Map the observation into its fields. Fill every field it defines.
- Do not invent fields the template does not ask for.
- State which template you chose and why (e.g., "Using bug_report.yml — only template present, matches bug kind").
- Use `gh issue create --template <name>` (verify the actual filename first).

**No template:** Use the fallback structure below.

## Step 2: Verify You Have a Real Observation

Ask: Can I point to a specific session, error message, trace, or behaviour I actually witnessed?

If no — there is no issue yet. Say so rather than inventing one. A suspicion is not a problem statement.

## Fallback Structure (No Template)

**Summary** — one sentence: expected vs. actual.
**Observed** — concrete behaviour: what was seen, exact error text or trace, where.
**Expected** — what should have happened.
**Context** — repro steps, version, commit. Only what was actually checked.
**Scope boundary** — what this issue is NOT about (optional but valuable).
**Open questions** — unknowns the implementer should verify. Every entry marked `[unverified]`.

## Uncertainty Rule

Every cause statement must be marked:

- `[verified: <how>]` — you checked; here is how
- `[unverified]` — you have not verified this

When you have not verified the cause, this sentence is **required**:
> "I have not verified the cause."

The implementer must inherit your doubt, not a false floor of confidence.

## The Issue Is Where "Why" Survives

The motivating problem and the name of whoever reported it exist in the issue or
nowhere: a commit records neither, and `git log` credits the implementer rather than
the reporter. Write the problem in the reporter's terms, and quote them where you can.
See **Writing for the archaeologist** below for what else is unrecoverable.

## Scope Rule: One Issue, One Observed Problem

If you notice a second suspected problem while writing: do not add it to the body. If you genuinely suspect it shares a code path, add exactly one line under Open Questions: `[unverified]: <suspected problem> may share this code path`. Open a separate issue for it after this one.

## Pull Request Descriptions

An issue is written before the work, for whoever picks it up. A PR description is
written after it, for **two** readers who need different things from the same
document:

- the **reviewer**, deciding this week whether to trust the diff;
- the **archaeologist** — anyone, including you, asking in two years why the code is
  like this.

The reviewer reads it once. The archaeologist is why it outlives the review.

Both are served by the same thing: it carries what the diff cannot. **Git history
shows how the change *was* made and never how it *wasn't*** — the alternative you
rejected, the scope you deferred, and the part you were least sure of exist nowhere
else.

### First: check for a template

```bash
ls .github/PULL_REQUEST_TEMPLATE.md .github/PULL_REQUEST_TEMPLATE/ 2>/dev/null
```

If the repo has one, **fill its sections**. It is the project's stated rule, so it wins
over the shape below — the same way an issue form wins in Step 1. Do not invent sections
it omits, and do not replace its headings with these. Where the template asks for
something this skill does not mention, the template still asks for it.

No template: use the shape below.

### Then: it describes the diff that exists

Write it with `git diff <base>..HEAD` open in front of you, not from what you set out
to do. Then re-read the description against the file list and delete every claim the
diff contradicts.

**If the diff contains something you no longer think should ship, change the diff.**
Do not describe it away. The specific failure this prevents is a "deliberately does
not do" entry naming something the diff *does* — the most dangerous sentence a PR body
can carry, because it reads as scrupulous honesty. A reviewer who spot-checks one such
claim stops trusting every other claim in the description, and they are right to.

### The shape

Where no template supplies one, five parts, in this order:

1. **What changes** — one sentence, the outcome for someone using the software. Not a
   tour of the files; the diff already lists those.
2. **Why this way** — the reasoning, and what you rejected. Only you can write this.
3. **Where to look first** — the reviewer's entry point: the riskiest hunk, the thing
   you are least sure of, and whether to read commit-by-commit or by file.
4. **What this deliberately does NOT do** — every deferral, each with an issue number
   that already exists. File them before opening; "follow-up later" is not tracking.
5. **What you ran** — the commands, and their result.

If the project links PRs to issues, reference the one this serves.

### Writing for the archaeologist

Someone will land on a line of code and ask why. The chain they follow is
**line → commit → pull request → issue → discussion**, and every hop is a link that
has to exist because you made it.

Two things break that chain in practice:

- **`git blame` usually lands on a refactor.** Reformatting, renames and code movement
  overwrite authorship, so the commit it finds is rarely the one that decided anything.
  The PR is where the reasoning is; blame is only the way in.
- **A prose mention is not a link.** "fixes the thing from #123" reads fine and is
  invisible to every tool that walks these relationships. Use the real closing
  reference (`Closes #123` in the PR body, or the UI's link), and for an epic use
  native sub-issues rather than a markdown checklist — the link is queryable, a
  checklist is prose.

Then write down the things that are **unrecoverable** if you don't. None of these can
be reconstructed from the diff by anyone, however careful:

| What | Why it vanishes |
|------|-----------------|
| The motivating problem | Never in a commit. It lives in the issue or nowhere. |
| Who asked for it | Commit authorship credits the implementer. Whoever reported it is invisible in `git log`. |
| The alternative you rejected | Leaves no trace at all — the code shows only what you chose. |
| What you deliberately did not do | Absence is indistinguishable from oversight. |
| Why something was **removed** | The hardest case: there is no code left to blame. |
| Whether it was a breaking change, and your reasoning | Conventional-commit markers are unreliable in both directions; the reasoning is the durable part. |

A decision recorded nowhere gets re-litigated, or quietly contradicted by someone who
never knew it was made. If a rejected alternative was genuinely load-bearing — you
expect someone to propose it again — it has outgrown the PR body and wants a decision
record the project keeps.

### Verification is a report, not a checklist

List only commands you actually ran. A `## Verification` block of plausible-looking
commands is the same defect as an unverified cause in an issue body: it manufactures a
floor of confidence the reader then builds on. Say plainly what you could not run, and
why.

### Annotate the diff; don't inflate the description

A question about one line belongs on that line. Comment on your own diff before
requesting review — that is where "this looks wrong but isn't, because…" goes. The
description carries what is true of the whole change; inline notes carry what is true
of one hunk.

### Size is part of reviewability

Review quality falls off with size: roughly 200 changed lines is the working target and
400 the practical ceiling, and past about 1000 reviewers find markedly fewer defects —
often leaving *fewer* comments, because attention is gone rather than because the code
is clean. Past the ceiling the fix is to split the change, not to write a longer
description.

### Remove before opening

| What you wrote | What to do instead |
|----------------|-------------------|
| "Deliberately does not do X" where the diff does X | Change the diff, or delete the claim |
| A `## Verification` block listing commands you did not run | List only what you ran; name what you skipped |
| `Closes #TBD`, or "issue to be filed" | File it first, then reference the real number |
| A file-by-file tour of the diff | One sentence on what changes, then where to look |
| The skill's five parts used where the repo ships a PR template | Fill the template's sections; it is the project's stated rule |
| "Refactored for clarity" | Name what was wrong before |
| The issue title restated as the summary | The issue states the problem; the PR states the resolution |
| "Should be safe" / "minor change" | Say what you checked, or say you did not check |
| "fixes the thing from #123" as the only link | Use a real closing reference; a prose mention is invisible to every tool that walks these links |

## Common Mistakes — Remove Before Posting an Issue

| What you wrote | What to do instead |
|----------------|-------------------|
| "Root cause is X; fix by doing Y" | `Cause: [unverified]` + observed behaviour only |
| Any sentence starting with "Fix by", "We should", "Refactor", "Add a", "The solution is" | Delete the sentence |
| "Import is probably similarly broken" | One line under Open Questions: `[unverified]: import may share this path` |
| Cause asserted without `[verified]` or `[unverified]` marker | Add the marker; add "I have not verified the cause" if unverified |
| Extra fields beyond the template | Fill only what the template defines |
| "This could cause issues" | Not a problem statement — has this been observed? |
| An "Additional context" section that introduces new problems | Open a separate issue; add one `[unverified]` line here if warranted |
| Implementation steps (numbered list of code changes) | Remove entirely |
