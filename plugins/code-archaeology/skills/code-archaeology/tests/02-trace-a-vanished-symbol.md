# 02 — Trace a vanished symbol

Real repository, `gh` authenticated, `git` and `gh` only, read-only.

> An internal planning document references an environment variable
> `MARKDOWN_VAULT_MCP_READY_TIMEOUT_S`. A user reports that setting it has no effect.
>
> **Work out what happened to it: does it still exist, was it renamed or removed, when,
> in which release, and why. If it was replaced, what replaced it, and was the change
> announced to operators?**
>
> Produce a written answer with your evidence. Say explicitly what you verified and what
> you are inferring.

Tests rename-following by content rather than path, release containment
(`git tag --contains`), and reading a changelog **at the tag** rather than at `HEAD` —
the entry announcing this change was later dropped by a mechanical regeneration, so the
present-day changelog does not mention it at all.

## Baseline
Correct and thorough: rename commit, date, PR, issue, the lost changelog entry, and the
absence of any operator-reachable record today. Made the unsupported claims "the old
name never appeared in the source of any released version" and "zero hits, all tags"
without establishing that its search space was complete.
