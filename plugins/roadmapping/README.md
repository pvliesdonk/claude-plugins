# roadmapping

Charting, refining and revisiting multi-epic technical roadmaps — work that
spans more than one pull request, where the order is not yet decided and the
edges are still vague.

A roadmap answers three questions: which direction, in what order, and what we
do not yet know. It does not answer *how*. The moment it answers how, it has
become a plan that will be wrong.

## Install

```
/plugin marketplace add pvliesdonk/claude-plugins
/plugin install roadmapping
```

## Why it exists

Planning skills have one resolution setting. Point them at six months of work
and they emit file paths and schemas for things nobody has looked at yet.
Reviewers correctly attack that precision, and the artefact loses credibility.
The fix is not to plan more carefully — it is to plan at a **declared**
resolution and defend it.

The core rule, from which everything else follows:

> If you do not have hard evidence, you cannot be certain. **It is not your job
> to obtain that evidence now.**

The second half is the one that gets ignored. On reaching a gap the tempting
move is to read the code until you can say something concrete — which is how
a roadmap fills with confident detail about unscoped work. So: **assert it, or
file it as a known unknown. Never research to promote it.** Every unknown
carries a *resolved-by* pointer, and where nothing planned resolves it and not
knowing changes what you do next, the finding-out becomes a research issue with
an appetite.

## What it enforces

- **Resolution is derived, never stored.** A milestone whose only open issue is
  its refinement issue is an idea; no agent may build from it.
- **Everything is work.** Research and refinement get issues in the same
  tracker, ordered by the same dependencies, so deferred evidence has an owner
  rather than vanishing.
- **Acceptance criteria are frozen through refinement.** Decomposition is lossy,
  and a criterion rewritten to match the features you happened to create is no
  longer a check on anything.
- **Provenance tags on every item** — `stated` / `derived` / `evidenced` —
  recording who owns a claim, so a later session does not cite agent synthesis
  back at the user as their own settled intent.
- **The tracker is working memory; the repo is the record.** A spike's working
  stays in the issue, its verdict in the closing comment, its consequence in the
  index.

Stop rules are explicit and refuse by name: no file paths or schemas at
direction resolution, no unknown without a resolved-by pointer, no research
issue without an appetite, no milestone due date, no state written into the
index.

## A note on milestones

This skill uses a GitHub **milestone as an epic — an idea being refined into
features**, each carrying an acceptance criterion and a refinement issue.

That is not the only convention. Many projects use a milestone as a **release
payload**, titled for a version, where "safe to cut this release" reduces to
"no open issues in that milestone". The two are incompatible, and mixing them
silently is the failure mode: a triage pass that treats milestones as release
commitments will strip a roadmap's milestones as speculative, and a release
gate that counts open issues will never go green against a milestone that
carries a permanent refinement issue.

Establish which convention a repository uses before applying either. The
companion `github-issues:triaging-issues` skill carries the same warning from
the other side.

## Handing off

When exactly one feature becomes next and is marked ready, this skill is
finished — hand to `superpowers:brainstorming` and then
`superpowers:writing-plans`, which are correct for a single unit of work.
A defect, or something wrong that needs investigating, is not roadmap work;
that is `github-issues:writing-issues`.
