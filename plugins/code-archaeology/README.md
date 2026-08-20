# code-archaeology

Working out **what happened and why**, from what a project left behind — before a
refactor or a removal, during a postmortem, while onboarding, or when a decision
nobody remembers making is being questioned again.

## Install

```
/plugin marketplace add pvliesdonk/claude-plugins
/plugin install code-archaeology
```

## Why it exists

Two agents were asked real questions about a real repository — *why does this tool
return empty instead of waiting*, and *what happened to this environment variable* —
using only `git` and `gh`. Both produced excellent answers: the right commits, the
right pull requests, the rejected alternatives, a careful verified-versus-inferred
split. One even found that a breaking-change entry had been silently destroyed by a
later mechanical changelog regeneration.

Both were also working in a **shallow clone**, and neither noticed.

Every key commit they cited was unreachable from `HEAD` — present only because tags
held the objects. The effect reproduces on any shallow clone: `git clone --depth 50` of
that repository reaches 305 commits from `HEAD` against 1269 from `--all`, and
`git log -S'READY_TIMEOUT_S'` returns 5 hits one way and 10 the other — four of those
ten being boundary artifacts that never touched the variable at all. Nothing errors. The
answers happened to be right, and would have been reported with identical confidence
had they been wrong.

That is the gap this skill fills. Not "cite your evidence" — good investigators already
do. **Establish that your search space is complete before you trust what you didn't
find.**

## What it covers

**Ground truth first.** A shallow clone lies about its own shape: the graft boundary is
parentless, so `git rev-list --max-parents=0 HEAD` reports a mid-history refactor as the
project's first commit. Check, unshallow, fetch tags, and choose scope deliberately.

**Finding versus proving absence.** "I found X" is safe on partial history. "X never
happened", "X was introduced in Y", "X is the only case" are claims about everything you
did *not* find, and are worthless without a search space you have proven complete.

**The chain, and where each hop breaks:**

- *line → commit* — blame lands on the refactor, not the decision. `-w -C -C -C`,
  `--ignore-rev`, and content search over path search, because paths break on renames
  and content survives them.
- *commit → pull request* — ask the API; a subject-line regex misses squashes and
  invents false hits.
- *pull request → issue* — **three indexes that each miss what the others catch.** A PR
  body reading `Refs #1055` returns zero from `closingIssuesReferences`, because `Refs`
  is not a closing keyword, while the issue's timeline shows that PR among 21
  cross-references.
- *issue → discussion* — the body states the problem; the comments hold the argument.

**When the trail is cold** — tests as the surviving record of intent, docs read at the
tag rather than at `HEAD`, sibling repositories, and the deleted code itself. Removal is
the hardest case because there is no code left to blame. Where nothing was written down,
"not recorded" is the answer; a plausible reconstruction is worse than a gap, because it
gets repeated as fact.

**Authorship is not authority.** A post under a maintainer's name may have been written
by an agent holding their token, and a maintainer-filed issue often restates an outside
contributor's words.

**Close the loop.** An answer that lives only in a chat log has not been recorded, and
the next person pays for it again.

## Assumes only git

Richer tools — a forge API, a code-intelligence server, decision records — are used when
present and named as optional where they appear. Where a project has something that
answers a question directly, use it; this is what to do when it does not.

## The other half

Archaeology is only possible if someone deposited the record. The companion
`github-issues` plugin is the deposit side: what belongs in an issue and a pull request
description so that this skill has anything to find — the motivating problem, who
reported it, the alternative rejected, and why something was removed, none of which any
diff can reconstruct.
