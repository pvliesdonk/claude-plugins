---
name: writing-agent-instructions
description: Use when writing, changing, reviewing or shortening the files an agent loads as instructions: AGENTS.md, CLAUDE.md, .claude/rules/*.md, GEMINI.md, .cursor/rules, a SKILL.md body, or a system-prompt fragment. Decides which sentences the agent can act on, where every other sentence goes, and how to compress a file without losing a rule.
---

# Writing Agent Instructions

An instruction file is read by a model at the start of every session (an
always-loaded file) or when it picks a task (a skill). Every sentence in it
competes with the task for attention, and a model follows what the file says
literally. The file is therefore written for the reader that acts on it, not
for the human who wants to know why.

## The Rule: Every Sentence Is a Directive, a Scope Limit or a Pointer

A sentence survives if the agent can act on it at the moment it reads it:

- **Directive**: an imperative with a concrete, verifiable object. `Run
  uv run ruff format . after ruff check --fix .`
- **Scope limit**: the condition or boundary of a directive. `Only for files
  under src/; tests keep their own formatter.`
- **Pointer**: where the agent finds what it needs next. `Release steps: the
  releasing skill.`

Everything else moves or goes: justification, enforcement narrative, history,
tutorial, a map of files the agent can list itself.

**STOP. Before you write or keep a sentence:**
> Am I about to explain why the rule exists, narrate how it is enforced, or
> soften it?

If yes: fold the why into one clause only if it lets the agent decide a case
the rule does not list, move the enforcement story to the check that enforces
it, and replace the softener with the condition it stands for.

**Never ask a model to "make it more concise."** It follows that instruction
literally and optimises length, and real directives go with the padding.
Compress by inventory (Mode B below), never by paraphrase.

This skill assumes nothing about the repo. Where the project states its own
rule (a budget test, a CONTRIBUTING.md section, a house style), that rule wins
and this skill is the fallback. Say which of the two you are in before you
start.

## Step 0: Know the Host

| Host | Always-loaded file | Loads on demand | Stated limit |
|------|--------------------|-----------------|--------------|
| Claude Code | `CLAUDE.md`, or `AGENTS.md` when no `CLAUDE.md` exists; `.claude/rules/*.md` without `paths`; every `@import` | rules with `paths:`; skills (name and description only until invoked) | target under 200 lines; longer files "reduce adherence" |
| Codex | the `AGENTS.md` chain from repo root to cwd, nearest last | nothing | 32 KiB, then truncated |
| Cursor | rules with `alwaysApply: true` | glob-attached, agent-selected, manual rules | under 500 lines per rule |
| Copilot | `.github/copilot-instructions.md`, nearest `AGENTS.md` | `.instructions.md` with `applyTo` | "no longer than 2 pages" |

Two facts hold on every host: the file is advisory, so a step that must run at
a fixed point (before every commit, after every edit) is a hook or a CI check,
not a sentence; and an `@import` or a nested file costs the same context as
inline text.

## Mode A: Adding or Changing a Rule

### 1. Three gates for the always-loaded file

A sentence goes in the always-loaded file only if all three hold:

1. **Applies to most tasks.** A rule for releases, migrations or one subsystem
   goes in a skill or a path-scoped rule.
2. **Not inferable from the repo.** The agent reads code, `pyproject.toml`,
   CI config and `--help`. A rule that restates them costs attention and buys
   nothing. Keep the one that departs from what the repo would suggest.
3. **Not already enforced by a check.** If a hook, linter or CI job fails on
   the violation, keep at most one line naming the command that runs it
   locally; the check's own message carries the rest.

Fails gate 1: write it in the skill or rule file for that task and leave one
pointer. Fails gate 2: delete it. Fails gate 3: keep the command, delete the
explanation.

### 2. Write the directive

- **Imperative, concrete, verifiable.** `Use 2-space indentation`, not
  `Format code properly`. `Run npm test before committing`, not `Test your
  changes`.
- **What to do, not what not to do.** `Write the result as prose paragraphs`,
  not `Do not use markdown`. Keep a `never` only where no positive form
  exists.
- **Condition, not hedge.** `prefer`, `consider`, `where possible`,
  `generally` are read as either absolute or optional. Write the case: `Run
  the single failing test; run the whole suite before you push.`
- **State the scope.** Current models do not generalise an instruction from
  one item to its siblings. `Every public function`, not `functions`.
- **One rationale clause, only when it decides an unlisted case.** `Never use
  ellipses: the output is read aloud by a text-to-speech engine` tells the
  agent what else to avoid. `Apply it deliberately, not by habit; the review
  is where a mistake gets caught` tells it nothing it can do. Keep the first
  kind, in the same sentence, under twenty words. Delete the second.
- **Emphasis on one line per file at most.** `IMPORTANT` on the one rule the
  agent keeps skipping. Bold, capitals and `MUST` on many lines mean none
  stands out. Strong language also over-triggers on current models: `Use X
  when Y`, not `CRITICAL: you MUST use X`.
- **A default with one escape hatch, not a menu.** `Use pdfplumber; for
  scanned PDFs use pdf2image with pytesseract.`
- **One term per concept** throughout the file.

### 3. Place it

- Earlier sentences carry more weight. Put the rule in the section that owns
  its topic, and the rule that matters most in the file first in its section.
- Before adding, grep the file and every other loaded file for the same topic.
  Two instructions that disagree make the agent pick one arbitrarily; merge or
  delete the older one in the same change.
- Count sentences added against sentences removed. A change that only adds
  needs a reason in its description.

## Mode B: Compressing a File Without Losing a Rule

### 1. Inventory before prose

```bash
# From the project root; the script reads only files under the working directory.
python3 "${CLAUDE_PLUGIN_ROOT}"/skills/writing-agent-instructions/scripts/sentences.py AGENTS.md > /tmp/before.tsv
```

Outside a plugin install, the script is `scripts/sentences.py` beside this
file. Tag every sentence in the output with one letter:

| Tag | Meaning | Fate |
|-----|---------|------|
| D | directive the agent can act on | keep, once |
| S | scope limit or condition of a D | keep, attached to its D |
| P | pointer to a file, skill, command or section | keep if the target exists |
| R | rationale: why the rule exists | one clause on its D, or delete |
| N | narrative: history, enforcement story, how the machinery works, what a human would want to know | delete, or move to the document it describes |
| H | hedge or softener | rewrite as a condition, or delete |
| X | inferable from the repo, or enforced by a check with no local command named | delete |

Write `inventory.md`: every D, S and P verbatim, grouped by section. This is
the contract for the rewrite. Do not start the rewrite until it exists.

### 2. Rewrite from the inventory

Work from `inventory.md`, not from the old prose. For each entry:

- Write the D once, in the section that owns its topic, in the form from
  Mode A step 2.
- Attach its S as the same sentence or the next one.
- Keep the P if its target exists; turn a sentence that lists what a script
  prints into a P at the script.
- Fold an R into its D only as a clause that decides an unlisted case.
- Move an N worth keeping to the design doc, reference, CONTRIBUTING.md or
  check message it describes, and say in the change description where each
  one went. Delete the rest.

Keep the section order the agent already knows unless a section has become
empty.

### 3. Prove nothing was lost

```bash
python3 "${CLAUDE_PLUGIN_ROOT}"/skills/writing-agent-instructions/scripts/sentences.py AGENTS.md.new > /tmp/after.tsv
```

For every line of `inventory.md`, name the sentence in `after.tsv` that
carries it. Put the mapping in the change description as a table: inventory
line, new location. An inventory line with no new location is a defect in
the rewrite, not a trim; restore it before anything else.

A D the repo enforces by a check may leave the file only if the check exists,
runs on the same event, and its failure message names the fix. Say which
check, by file and job name.

### 4. Measure against the host

Report lines and characters before and after, and the host's limit from
Step 0 or the project's own budget test. The budget is a ceiling; a file at
the ceiling has no room for the next rule, so aim for the host's target.

### 5. Verify behaviour, not length

Pick one task that depends on a rule you moved or rewrote and run it in a
fresh session. One run proves nothing either way; where it matters, run
several and compare with the old file. A rule the agent now skips goes back
in, in its old position, and the compression is rejudged from there.

## Where Each Kind of Sentence Goes

| Sentence | Belongs in |
|----------|------------|
| Command the agent cannot guess, with its order and flags | the always-loaded file |
| Convention that departs from the language or tool default | the always-loaded file |
| Gotcha: a non-obvious behaviour that costs a wasted run | the always-loaded file, as the directive that avoids it |
| Procedure for one kind of task (release, migration, review) | a skill or path-scoped rule, with one pointer in the always-loaded file |
| Why a convention exists | one clause on its directive when it decides unlisted cases; otherwise the design doc or decision record |
| How a check enforces the rule, and what fails without it | the check's own failure message; CONTRIBUTING.md for humans |
| Which files hold which sentinel blocks, which versions must match, what a script reports | the script's output, pointed at by one line |
| Map of the repository, file by file | nowhere; the agent lists files itself |
| Tutorial, worked example of a routine task | a skill, or nowhere |
| Step that must run every time | a hook or CI job, not a sentence |

## Common Mistakes

| What you wrote | What to do instead |
|----------------|-------------------|
| "Make it more concise" as an instruction to a model | Run Mode B: inventory, rewrite, mapping table |
| "This is not style policing: the tool silently ignores a subject whose type it does not count" | `PR titles use one of: build, chore, …; the PR Title job fails otherwise.` Move the rest to the job's failure message |
| "Apply it deliberately, not by habit; the review is where a mistake gets caught, but the reviewer should never have to" | Delete; it decides nothing |
| "Prefer running single tests where possible" | `Run the single failing test; run the whole suite before you push.` |
| "**ALWAYS** run format after check" on one of twelve bold lines | Un-bold the other eleven; keep one |
| A 1,700-character sentence enumerating every file and its sentinel block | One line: `Run scripts/check_template_conformance.py; it lists every line outside a sentinel block.` |
| "The accepted set lives in X; that list, the counted subset and this prose are checked against each other by Y" | `Accepted types: scripts/check_pr_title.py.` The lockstep test is the test's concern |
| A rule the agent already follows without it | Delete; add a hook if it must never slip |
| Two sections that each state the issue-linking rule differently | One statement, in the section that owns PRs |
| "Consider using a subagent for large investigations" | `Use a subagent when an investigation would read more than ten files.` |
| A rule for one subsystem in the root file | Move it to a path-scoped rule or a skill; leave a pointer |
| A SKILL.md that opens with three paragraphs on why the skill exists | Open with the rule and the first step; the why goes in the plugin README |

## Review Checklist

Read the file as the agent that will act on it.

- Is every sentence a D, S or P? Tag the rest and apply the table.
- Does any sentence restate code, config or a tool's own help?
- Does any sentence narrate a check instead of naming its command?
- Is each rule stated once, in the section that owns it, with no sibling
  that disagrees?
- Is every `prefer`, `consider`, `generally`, `where possible` a condition?
- Is emphasis on at most one line?
- Does each rationale clause decide a case the rule does not list?
- Is the file under the host's target, with room for the next rule?
- After a compression: does the change description carry the inventory
  mapping, and is every moved N named with its destination?

## Evidence

The claims this skill rests on, with their sources, are in `evidence.md`
beside it; it stands on its own. The dated reference it condenses, with
every quotation, is `docs/design/reference/agent-instruction-files.md` in
`pvliesdonk/fastmcp-server-template`. Read one of them before arguing with a
rule here.
