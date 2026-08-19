---
name: writing-issues
description: Use when filing a bug, opening or creating a GitHub issue, drafting a ticket, writing up a finding or observation as an issue, or when a code review or brainstorm surfaces a problem worth tracking.
---

# Writing Issues

## The Rule: Observation, Not Work Order

You are recording what was observed. You are not diagnosing, designing, or prescribing.

**STOP. Before writing a single word:**
> Am I about to describe how to fix this, propose an architecture, or assert a root cause?

If yes — **remove it.** The issue body must contain no proposed approach and no asserted cause. An issue that reads like a work order misleads implementers into treating your imagination as researched fact.

Companion skill: `github-issues:triaging-issues` covers what to do with an issue that already exists — labels, priority, milestone, closing. Filing is this skill; classifying is that one. Do not label or milestone as part of filing beyond what the issue form applies.

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

## Scope Rule: One Issue, One Observed Problem

If you notice a second suspected problem while writing: do not add it to the body. If you genuinely suspect it shares a code path, add exactly one line under Open Questions: `[unverified]: <suspected problem> may share this code path`. Open a separate issue for it after this one.

## Common Mistakes — Remove Before Posting

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
