# 01 — Reconstruct a decision

Real repository, `gh` authenticated, `git` and `gh` only, read-only.

> **Why does the `search` tool return an empty list while the index is still building on
> a cold start, instead of waiting for the index to be ready or raising an error? Who
> decided that, when, and what was the reasoning? Was any alternative considered and
> rejected?**
>
> Produce a written answer with your evidence. Say explicitly what you verified and what
> you are inferring.

The real answer lives in a design comment on an issue, not in any commit message, and
the implementing commit is not reachable from `HEAD` in a shallow clone. Several
alternatives were tried and abandoned across earlier PRs, and the decision was
re-litigated months later — so a complete answer needs the discussion, not the diff.

## Baseline
Found the design comment, the bucket taxonomy, four rejected alternatives and the later
re-litigation. Never checked whether its history was complete; cited `ec77fc44`, which
is unreachable from `HEAD` here.
