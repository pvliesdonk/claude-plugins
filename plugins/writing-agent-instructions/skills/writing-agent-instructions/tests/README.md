# Pressure scenarios for `writing-agent-instructions`

Run each against a fresh subagent, once WITHOUT the skill and once WITH it. The
fixture is any repository with an `AGENTS.md` or `CLAUDE.md` over 150 lines
that mixes rules with their justification; the one these were written from
is `pvliesdonk/fastmcp-server-template`'s `AGENTS.md.jinja` (252 rendered
lines, 23,522 characters against a 24,000-character budget).

## The baseline failure these were written from

A fresh session was asked to make that file "more concise" with no other
guidance. Observed, one run:

    before  23,522 chars  164 sentences
    after   20,007 chars  130 sentences   (-15 percent)
    code spans lost: 17, all abbreviations of a list that survived
    directives lost: none found by phrase check

What the run did not report:

- The revert rule changed meaning. Original: the title job warns on either
  revert form. Rewritten: the quoted form "passes with a warning
  annotation; `revert:` passes silently". A modification, not an omission,
  inside a paragraph presented as tightened wording.
- The 1,055-character sentinel enumeration became an 879-character one.
  Nothing moved out of the file; enforcement narrative and justification
  stayed, shorter.
- Its own verification was the strings `tests/test_commit_conventions.py`
  and the template's CI pin, then "no rule was dropped". No before or after
  inventory existed to support that sentence.

The failure is not weak compression. It is **an unverifiable claim of
preservation**: a paraphrase can rewrite a rule without deleting one, and the
report had no artefact a reviewer could check it against.

Asked to add a rule, a model writes a paragraph: the rule, why it exists,
which tool would silently misbehave without it, and which test keeps the
prose and the tool in lockstep. The "PR Title" paragraph in scenario 2 is
such a paragraph as it stands in the file today; one sentence of five is a
directive.

## Scenarios

- `01-make-it-concise.md`: the compression request. Rewards an inventory
  before the rewrite and a mapping table after it, with no lost directive.
- `02-add-a-rule.md`: a new rule arrives with its history. Rewards one
  directive and one pointer, with the history sent where it belongs.
- `03-hedged-rule.md`: a rule written with `prefer` and `where possible`.
  Rewards a condition in place of the hedge and no new emphasis.

## Pass criteria (all)

- Names the host and its limit before changing anything.
- Every sentence written is a directive, a scope limit or a pointer; any
  rationale is one clause that decides an unlisted case.
- A compression shows the inventory mapping; a lost directive is treated as a
  defect, not a trim.
- Enforcement narrative is moved to the check or deleted, and the change
  description says where.
- No sentence asks the next model to "be concise".
