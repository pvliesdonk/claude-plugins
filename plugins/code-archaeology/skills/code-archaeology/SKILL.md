---
name: code-archaeology
description: Use when you need to work out why code is the way it is, what happened to something that no longer exists, when a behaviour changed and in which release, or what happened across a range of history and why — before a refactor or a removal, during a postmortem, while onboarding, or when a past decision is being questioned or re-litigated.
---

# Code Archaeology

Working out **what happened and why**, from what the project left behind.

Two shapes, one discipline. **Point questions**: why is this line like this, what
happened to the thing that used to be here, when did this behaviour change.
**Range questions**: what happened between these two points, and why. Both are
answered from the same chain of records, and both fail the same way — a confident
answer built on a search that was never complete.

**This skill assumes only `git`.** Everything richer — a forge API, a code-intelligence
tool, decision records — is used when present and named as optional where it appears.
Where a project has a tool that answers a question directly, use it; this is what to do
when it does not.

## The Rule: Evidence or Silence

Every causal claim traces to something you read, and you say which. Mark each one
`[verified: how]` or `[unverified]`.

A claim you cannot source is **dropped, not hedged**. Confabulated history is worse
than a gap, because it is plausible, it gets repeated, and the next person inherits it
as fact. "Not recorded" is a complete and respectable answer.

## Step 0: Establish Ground Truth — Before Any Query

Run this first, every time. It is the difference between an answer and a guess:

```bash
git rev-parse --is-shallow-repository   # true = every history answer below is truncated
git rev-list --count HEAD               # vs...
git rev-list --count --all              # ...everything the object store actually holds
```

**The shallow-clone trap, measured on a real repository:** 163 commits reachable from
`HEAD`, 1637 from `--all`. The same pickaxe query returned **1 hit scoped to `HEAD` and
11 with `--all`**. Nothing warned; both answers looked authoritative.

Worse, a shallow clone lies about its own shape: the graft boundary is parentless, so
`git rev-list --max-parents=0 HEAD` reports a mid-history refactor as the project's
first commit. An archaeologist who trusts it dates the project from a commit that is
nowhere near the beginning.

**And it does not only hide evidence — it manufactures it.** A boundary commit has no
parent, so git renders its *entire tree* as newly added, and a pickaxe matches it for
every string in the repository. Measured: on a shallow clone, `git log --all -S'<var>'`
returned ten commits, four of them boundary commits reporting "275 files changed, 94,482
insertions(+)". None of those four ever touched the variable, and the two commits that
actually introduced and renamed it were absent entirely. The naive reading — that the
variable arrived in a docs commit — is confidently wrong rather than merely incomplete.

Spot them by cross-checking the hits against the boundary list:

```bash
comm -12 <(git log --all --format=%H -S'<string>' | sort) <(sort .git/shallow)
```

Any overlap means those hits are artifacts. Deepen the clone and re-run.

So, before trusting anything:

```bash
git fetch --unshallow    # or: git fetch --depth=<n> to go deeper
git fetch --tags         # tags hold objects HEAD cannot reach — often the ones you need
```

**Both of those are writes.** They download objects and `--unshallow` deletes
`.git/shallow`, permanently changing what every later query in that clone can see. They
do not touch the working tree, `HEAD`, or any ref tip — but if you were asked for a
read-only investigation, this is not covered by that permission. Ask first. If you
cannot write, you have two honest options: query the forge API instead, which sees the
full history regardless of your clone, or proceed on partial history and scope every
claim to it — which means making no negative or superlative claims at all.

Then decide scope deliberately. `--all` searches every ref; `HEAD` searches one line of
descent. In a repo with any release history, **default to `--all`** and say which you
used.

### Finding vs. proving absence

This distinction governs how much ground truth you need:

- **"I found X"** — safe on partial history. Finding something proves it exists.
- **"X never happened"**, **"X was introduced in Y"**, **"X is the only case"** — these
  are claims about *everything you did not find*, and they are worthless without a
  search space you have proven complete.

Before writing a negative or a superlative, state how you established completeness. If
you cannot, weaken the claim to what you actually saw.

## The Chain

Someone lands on a line and asks why. The trail runs:

**line → commit → pull request → issue → discussion**

Each hop breaks in its own way.

### line → commit: blame lands on refactors

`git blame` attributes the *last* change, which is usually a rename, a reformat, or a
move — not the commit that decided anything.

```bash
git blame -w -C -C -C <file>          # ignore whitespace; follow moved & copied code
git blame --ignore-rev <sha> <file>   # skip a known reformat
# repos may ship .git-blame-ignore-revs; wire it with:
git config blame.ignoreRevsFile .git-blame-ignore-revs
```

**Content beats path.** Paths break on renames; content survives them:

```bash
git log --all -S'<exact string>' --oneline    # pickaxe: commits that add/remove it
git log --all -G'<regex>' --oneline           # commits whose diff matches
git log --all --follow -- <path>              # follow a file across renames
git log --all --diff-filter=D -- <path>       # when was it deleted
git show <sha>^:<path>                        # read a file as it was before a commit
```

A path search for a renamed symbol returns nothing and looks like an answer. The
pickaxe finds the rename commit itself.

### Which release did it ship in

```bash
git tag --contains <sha> | sort -V | head -1   # earliest tag containing it
git describe --contains <sha>
```

This answers "does the version I'm running have this" — usually the question behind the
question.

### commit → pull request

```bash
gh api "repos/OWNER/REPO/commits/<sha>/pulls" --jq '.[].number'
```

Ask the API. Do not regex `(#123)` out of the subject: squash subjects sometimes lack
it, and passing mentions produce false hits.

### pull request → issue: three indexes, and each misses what the others catch

This is the hop people get wrong, because they use one index and believe it.

| Index | Catches | Misses |
|---|---|---|
| `closingIssuesReferences` (GraphQL) | closing keywords: `Closes`, `Fixes`, `Resolves` | `Refs #N` and every other non-closing mention |
| timeline `cross-referenced` events | prose mentions **and** links made in the UI | little — the widest net |
| grepping the body text | prose mentions | UI-made links, which have no text form at all |

Measured on a real repository: a PR whose body reads `Refs #1055` returns **zero**
linked issues from `closingIssuesReferences`, because `Refs` is not a closing keyword —
while the issue's timeline shows that PR among 21 cross-references. Four of five recent
PRs there had zero closing links.

```bash
# widest net: what has ever pointed at this issue
gh api "repos/OWNER/REPO/issues/<n>/timeline" --paginate \
  --jq '[.[]|select(.event=="cross-referenced")|.source.issue.number]|unique'
```

### issue → discussion

The reasoning is usually in the **comments**, not the body: the body states the problem,
the comments contain the argument, the objection, and the decision. Read the whole
thread, and read the linked threads it points to.

## Range Questions

For "what happened between A and B, and why":

1. **Enumerate through the API, not local git** — a shallow or stale clone silently
   truncates the range. `gh api "repos/OWNER/REPO/compare/A...B"`, paginated.
2. **Group by structure before reading deeply.** Epics, milestones, and labels already
   encode which changes were one story. Where none exist, group by subject — do not
   invent structure that isn't there.
3. **Fan out, one investigation per theme.** A single reader holding an entire range
   regresses to summarising commit subjects, because reading the linked discussions does
   not fit alongside synthesising them.
4. **Attribute from issue authorship.** `git log` credits whoever implemented it.
   Whoever *reported* it — often the only outside contributor involved — appears
   nowhere in the commit history.

## When the Trail Is Cold

Often nothing was written down. Say so plainly, then look where evidence still hides:

- **Tests are the best surviving record of intent.** A test names the case someone
  cared about, and a deleted test is a decision.
- **The deleted code itself** — `git show <sha>^:<path>` — plus the commit that removed
  it. (In a shallow clone this fails with `invalid object name` at the graft boundary,
  because the boundary commit has no parent — another reason Step 0 comes first.) Removal is the hardest case precisely because there is no code left to blame.
- **Docs at the tag, not at HEAD** — `git show <tag>:<path>`, or the forge's raw
  content API at that ref. Present-day docs have been edited by later decisions.
- **Sibling repositories** — a template, a shared library, an upstream fork often
  carries the discussion that this repo only inherited.
- **Release notes and changelogs at the tag.** These get rewritten: a later mechanical
  regeneration can silently drop an entry that existed at the time. If a changelog
  looks thin for a change you know was breaking, check it at the tag as well as at HEAD.

**Authorship is not authority.** A post under a maintainer's name may have been written
by an agent using their token, and an issue filed by a maintainer may be restating an
outside contributor's words. Check for an automation signature before treating a
comment as a human decision, and cite the artifact where the words first appear.

## Close the Loop

Archaeology that is not written back is paid for again by the next person. Once you
have an answer, put it where the next search will find it:

- a decision the project keeps — a decision record, an ADR, or whatever it uses;
- a comment on the issue or PR you excavated, so the trail is shorter next time;
- a test, if the finding is a behaviour nobody had pinned;
- and the durable half in the code's own documentation, if it explains something a
  reader cannot infer.

An answer that lives only in a chat log has not been recorded.

## Common Mistakes

| What happened | What to do instead |
|---|---|
| Ran history queries without checking for a shallow clone | `git rev-parse --is-shallow-repository` first; `--unshallow` before trusting anything |
| Trusted pickaxe hits on a shallow clone | Boundary commits match every string; cross-check hits against `.git/shallow` |
| Ran `--unshallow` during a read-only investigation | It is a write. Ask, or use the forge API, or scope your claims to the history you have |
| Scoped to `HEAD` and reported a complete answer | Use `--all`, and say which scope you searched |
| "This never existed" / "first introduced in X" from a partial search | Prove the search space, or weaken the claim |
| Took `git blame` at face value | `-w -C -C -C`; the first result is usually a refactor |
| Searched by path for a renamed thing, found nothing, concluded nothing | Pickaxe the content: `git log --all -S'...'` |
| Used `closingIssuesReferences` alone and found no linked issues | Also read the timeline cross-references and the body text |
| Read the issue body and stopped | The reasoning is in the comments |
| Filled a gap with a plausible reconstruction | "Not recorded" is the honest answer |
| Treated a post under a maintainer's name as their decision | Check for an automation signature; cite where the words first appear |
| Answered brilliantly in chat and moved on | Write it back — an unrecorded finding is rediscovered at full price |
