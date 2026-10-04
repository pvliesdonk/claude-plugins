# writing-agent-instructions

Write, review and shorten the files an agent loads as instructions, so that
every sentence is one the agent can act on, and compress such a file without
losing a rule.

## Install

```
/plugin marketplace add pvliesdonk/claude-plugins
/plugin install writing-agent-instructions
```

## Why it exists

A template repository's `AGENTS.md` reached 23,522 of its 24,000-character
budget. Adding one two-sentence rule meant deleting two sentences elsewhere.
The longest sentence ran to over 1,000 characters, enumerating every
re-rendered file and its sentinel blocks. Around the rules sat the reasons
for them, the story of which CI job enforces each one, and reassurance for a
human reader ("this is not style policing").

A fresh session was asked to make that file more concise, with no other
guidance. It returned the file 15 percent shorter (23,522 to 20,007
characters), kept every command and every directive a span-by-span diff
could find, and reported "no rule was dropped". Two things it did not say:

- One rule now means something else. The original says the title check
  warns on either revert form; the shortened file says the quoted form
  "passes with a warning annotation" and the `revert:` form "passes
  silently". No instruction was deleted; one was rewritten into a claim the
  source never made, inside a paragraph that reads as a faithful tightening.
- The prose it could not classify stayed where it was. The sentinel
  enumeration is still 879 characters, the enforcement narratives are still
  in the file, and its own check of the result was the strings the test
  suite pins, which is the floor a reviewer would check too.

That is the pair of gaps this skill closes. A model asked to be concise
paraphrases, and a paraphrase can change a rule without deleting a sentence,
so a word diff and a "nothing dropped" report prove nothing. And without a
tag on each sentence saying what it is for, a model has no basis to move the
narrative out of the file; it can only shorten it in place.

One run, with one model, is the observation behind this. The maintainer's
own experience with earlier models, the one that prompted the skill, was
rules deleted outright. Both failures have the same fix: an inventory of
what the file commits the agent to, written before the rewrite and checked
after it.

## What it covers

**The rule.** A sentence stays if it is a directive the agent can act on, a
scope limit on one, or a pointer to what it needs next. Rationale is one
clause, kept only when it decides a case the rule does not list. Enforcement
narrative goes to the check that enforces it. Hedges become conditions.
Emphasis goes on one line per file.

**Three gates for the always-loaded file.** Applies to most tasks; not
inferable from the repository; not already enforced by a check. A sentence
that fails one goes to a skill, a path-scoped rule, a hook, or nowhere.

**Compression by inventory.** Split the file into sentences with the bundled
`scripts/sentences.py`, tag each one, write out every directive and scope
limit verbatim, rewrite from that list, and prove with a mapping table that
each one has a new home. A directive with no home is a defect, not a trim.

**The host's limits.** Claude Code targets under 200 lines and loads imports
at full cost; Codex truncates the `AGENTS.md` chain at 32 KiB; Cursor keeps a
rule under 500 lines; Copilot allows two pages. A hook is deterministic; the
file is advisory.

## Evidence

The skill's claims come from the Claude Code and Claude platform
documentation, agents.md, the Agentic AI Foundation's measurement post, the
Codex, Cursor and Copilot instruction docs, and six published studies
(IFScale, ScaledIF, Agent READMEs, Lulla et al., Gloaguen et al., Shepard
and Albrecht). `evidence.md` beside the skill lists them with links; the
dated reference with every quotation is
[`agent-instruction-files.md`](https://github.com/pvliesdonk/fastmcp-server-template/blob/main/docs/design/reference/agent-instruction-files.md)
in the template repository.

Two things the sources do not settle, and the skill says so: whether a hedge
is read as absolute or optional, and the adherence cost of rationale
sentences as such.

## Assumes nothing about the repo

Where a project states its own rule, a budget test, a CONTRIBUTING.md section,
a house style, that rule wins and this skill is the fallback.
