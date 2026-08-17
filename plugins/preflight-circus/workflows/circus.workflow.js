// circus.workflow.js — the preflight circus: the gate a change passes before
// its push.
//
// Prompt source of truth. The lens and scorer prompts below are held here
// verbatim. The canonical upstream wording is the `code-review` plugin's own
// command prompt — commands/code-review.md in anthropics/claude-plugins-official
// — and wins on any disagreement; this script mirrors it for pre-push use
// against a local BASE..HEAD range.
//
// Changing the confidence threshold is not a one-line edit. See
// CONFIDENCE_THRESHOLD below before you touch it.

export const meta = {
  name: 'preflight-circus',
  description: 'Blind six-lens pre-flight gate over BASE..HEAD that keeps AI-induced technical debt out of the repository',
  whenToUse: 'Must pass before any push that creates or updates a PR. Invoked by the preflight-circus skill.',
  phases: [
    { title: 'Lenses', detail: 'six core lenses plus installed pr-review-toolkit agents, blind, in parallel' },
    { title: 'Score', detail: 'Haiku confidence score per finding' },
  ],
}

// The score a finding must reach to survive. This constant is the behaviour:
// it is read by the filter and by the summary log, and nowhere else.
//
// HAZARD, if you change it. Seven copies of this number live inside the
// PROMPTS bodies below — one calibration paragraph per core lens, plus the
// scorer's own rubric — and they cannot reference this constant, because they
// are prompt text handed to an agent rather than code. They are not
// narration: each one tells its lens where the bar sits so it self-censors
// below it. Lower this to 75 without sweeping them and every lens keeps
// calibrating against 80 — it withholds findings this script now stands ready
// to accept, and nothing errors, nothing logs, and the run still reports
// clean. Grep the prompt bodies and fix all seven in the same change.
//
// `meta` above deliberately does not state the number. It must be a pure
// literal, so it could only ever hold a hand-typed copy, and a reader of the
// description does not act on it.
const CONFIDENCE_THRESHOLD = 80

const PROMPTS = {
  "lens-1-claude-md": {
    body: `You are **Lens 1** of a six-lens pre-flight code review circus. Your job
is to audit a code change for adherence to CLAUDE.md files at every level
that applies to the modified files.

## Range to review

- Base SHA: \`{BASE}\`
- Head SHA: \`{HEAD}\`
- Modified files: \`{MODIFIED}\`

\`\`\`bash
git diff --stat {BASE}..{HEAD}
git diff {BASE}..{HEAD}
\`\`\`

\`{MODIFIED}\` is a convenience copy of the file list, not the authority on
it — it is caller-supplied and can arrive truncated or hand-trimmed.
\`{BASE}\` and \`{HEAD}\` already determine the list exactly, so derive your
own and work from that:

\`\`\`bash
git diff --name-only {BASE}..{HEAD}
\`\`\`

## CLAUDE.md files to load

CLAUDE.md is *guidance for the writer*, not all rules are reviewable
post-hoc — but explicit rules ("never X", "always Y", "must Z", "do not Z")
are. Locate every CLAUDE.md file applicable to the changed files:

1. **Root CLAUDE.md** at the repo root (if present).
2. **Per-directory CLAUDE.md** for each directory whose files appear in
   the diff. Walk upward from each modified file's directory to the root,
   loading every CLAUDE.md encountered.
3. **User-global CLAUDE.md** at \`~/.claude/CLAUDE.md\`. This path is outside
   the repository and not version-controlled — read it from the real
   filesystem, not via git.

For 1 and 2, list the tracked candidates at \`{HEAD}\`:

\`\`\`bash
git ls-tree -r {HEAD} --name-only | grep -iE '(^|/)CLAUDE\\.md$'
\`\`\`

That command lists the tracked set, and it runs inside your own worktree.
Keep its output — you subtract it below.

A CLAUDE.md can also be gitignored but still active — a gitignored
\`.claude/CLAUDE.md\` is the common case — so sweep for the untracked ones
too.

**Do not sweep the current directory.** You are running inside a
\`git worktree\` checkout, and a worktree checkout materializes *only tracked
files*. Untracked and gitignored files do not exist here at all, so a sweep
of \`.\` finds nothing every time and would let you report on an incomplete
rule set. Sweep the main checkout instead.

**Sandbox constraint. Do not "simplify" the steps below back into a
\`git -C "$MAIN" ls-files --others\` one-liner.** The worktree isolation
refuses any git command redirected at the shared checkout (\`-C\`,
\`--git-dir\`, \`--work-tree\`), and refuses compound commands it cannot
statically verify stay inside the worktree. It does not refuse a plain
filesystem read of an absolute path outside the worktree. So git runs only
inside your own worktree here, and everything outside it is reached with
\`find\`. The one-liner looks obvious and is refused every time.

Each step below is its own separate command:

- **Recover the git common directory.** Nothing else on the line — no
  \`dirname\` wrapper, no command substitution, no assignment:

  \`\`\`bash
  git rev-parse --path-format=absolute --git-common-dir
  \`\`\`

- **Derive the main checkout.** Read that output and take its parent
  directory — drop the trailing \`/.git\`. Derive it by reading, not by
  wrapping the previous command: shell state does not survive between
  commands, and the wrapped form is the shape that gets refused as
  unverifiable.

- **List the on-disk set.** Substitute the literal path you just derived
  for \`<MAIN>\`:

  \`\`\`bash
  find <MAIN> -name .git -prune -o -name worktrees -prune -o -name .worktrees -prune -o -iname 'CLAUDE.md' -print
  \`\`\`

  No \`-maxdepth\`. A CLAUDE.md six directories down is an active rule file
  like any other, and a depth limit drops it silently.

  Both worktree spellings are pruned. A sibling worktree checked out under
  the main checkout holds its own tracked copy of every CLAUDE.md; that copy
  is not in your \`git ls-tree\` list at that path, so without the prune the
  subtraction below would file it as an untracked rule file and you would
  review against a stale duplicate.

- **Subtract the tracked set yourself.** Strip the \`<MAIN>/\` prefix from the
  \`find\` paths, then remove every path the \`git ls-tree\` listing above
  already named. What remains is the untracked and gitignored set. No git
  command points outside your worktree at any point in this procedure.

Keep the remaining paths that sit at a 1 or 2 location (repo root, or an
ancestor directory of a modified file) and read them from disk at
\`<MAIN>/<path>\`. Note in your output that they are not part of \`{HEAD}\`.

This \`<MAIN>\` detour is *only* for untracked and gitignored files. Tracked
content must still be read by explicit rev — never from the main checkout's
working tree, which carries uncommitted changes that are not in the range
under review.

Read each applicable in-repo file (1 and 2): \`git show {HEAD}:<path>\` for
files tracked at \`{HEAD}\`, or \`<MAIN>/<path>\` from disk for the untracked
ones just found. Read the user-global file (3) directly from disk. Then for
each explicit rule, check whether the diff complies.

## What to flag

- Explicit rule violations introduced by the diff.
- New code that contradicts patterns documented in CLAUDE.md. Example: a
  rule says "domain hooks only, no override kwargs" and the new kwarg is
  an override → flag.
- New code that drifts from conventions documented in CLAUDE.md.
- Test-related rules (e.g. "integration tests must hit a real database")
  when the diff modifies tests.

## What NOT to flag

- Implicit conventions not documented in CLAUDE.md (those belong to other
  lenses, or to no lens).
- Style nits (formatting, naming) unless an explicit rule covers them.
- Issues that linters / typecheckers / CI would catch.
- Pre-existing issues on lines the diff did not touch.
- Rules that are clearly "guidance for writing new code" rather than
  reviewable invariants (e.g. "default to writing no comments" is a
  writer-side default, not a review-time blocker for a comment that
  explains a non-obvious why).`,
    calibration: `The scoring agent will filter on confidence ≥ 80 — only report issues you
are reasonably sure are real CLAUDE.md violations, not loose
interpretations.`,
  },
  "lens-2-shallow-diff": {
    body: `You are **Lens 2** of a six-lens pre-flight code review circus. Your job
is a shallow scan of the diff hunks for obvious bugs.

**This lens is intentionally diff-only.** Do not load surrounding file
context, do not follow callers/callees, do not read git history, do not
read other files in the repo. Your strength is fast pattern recognition
on the patch hunks; other lenses cover the deeper context.

## Range to review

- Base SHA: \`{BASE}\`
- Head SHA: \`{HEAD}\`

\`\`\`bash
git diff {BASE}..{HEAD}
\`\`\`

## What to flag (visible in the diff alone)

- **Logic errors** — inverted conditions, wrong operators, off-by-one,
  wrong comparison.
- **Null / None / undefined handling missing** where the diff clearly
  dereferences a value that might not exist.
- **Resource leaks** — files, connections, or other resources opened in
  the diff without a matching close / context manager.
- **Race conditions** visible in the diff (e.g. check-then-act on shared
  state without locking).
- **Security issues** visible in the diff — SQL injection, command
  injection, path traversal, secrets in plaintext, untrusted input
  flowing to a dangerous sink.
- **Obvious typos that change semantics** — e.g. \`=\` vs \`==\`, \`or\` vs
  \`and\`, \`>=\` vs \`>\`.
- **Exception handling that swallows errors silently** (bare \`except:\`,
  \`except Exception: pass\`) visible in the diff.

## What NOT to flag

- Style nits (formatting, naming, import order).
- Issues that require reading surrounding code, callers, or callees
  (those are other lenses' jobs — leave them alone).
- Issues a linter, typechecker, or CI would catch (formatting, pedantic
  style, unused imports, type errors caught by mypy/tsc).
- Pre-existing issues on lines the diff did not modify.
- General code-quality opinions (poor naming, lack of abstraction, etc.).
- Test coverage gaps (that's \`pr-test-analyzer\`'s job).`,
    calibration: `The scoring agent will filter on confidence ≥ 80 — only report bugs you
are reasonably sure will hit in practice. False positives at this lens
are common; bias toward not-flagging when uncertain.`,
  },
  "lens-3-git-history": {
    body: `You are **Lens 3** of a six-lens pre-flight code review circus. Your job
is to read git history on the modified files and flag bugs that are only
visible in historical context.

## Range to review

- Base SHA: \`{BASE}\`
- Head SHA: \`{HEAD}\`
- Modified files: \`{MODIFIED}\`

\`\`\`bash
git diff {BASE}..{HEAD}
# Then for each modified file:
git log -p --follow {HEAD} -- $FILE
git blame {HEAD} -L <hunk range> -- $FILE
\`\`\`

\`{MODIFIED}\` is a convenience copy of the file list, not the authority on
it — it is caller-supplied and can arrive truncated or hand-trimmed.
\`{BASE}\` and \`{HEAD}\` already determine the list exactly, so derive your
own and iterate over that:

\`\`\`bash
git diff --name-only {BASE}..{HEAD}
\`\`\`

You should \`git log -p --follow {HEAD}\` each modified file to see how the
relevant regions have evolved as of the head under review, and
\`git blame {HEAD}\` the specific lines the diff touches to see *why* the
current state exists.

## What to flag

- **Re-introductions of previously-fixed patterns.** If \`git log -p\`
  shows a prior commit that removed a problematic pattern (e.g. "fix:
  remove bare except"), and the new diff puts the pattern back, flag it.
  Cite the prior commit SHA and message.
- **Contradicted stated intent.** If a recent commit message says "going
  forward we always do X" or "never do Y", and the new diff violates
  that, flag it. Cite the commit.
- **Reversion of recent intentional change without justification.** If a
  recent commit changed A → B with a clear "why" in its message, and the
  new diff goes back to A, flag it. The reversion may be intentional —
  flag it so the human confirms.
- **Bug fixes silently reverted.** If \`git blame\` on a touched line
  points to a commit titled "fix:", "bugfix:", or with a CVE/issue
  reference, and the new diff undoes that fix, flag it.
- **Recently-flagged code being re-introduced.** If the file has a commit
  with "review:" or "address review:" in the message that established a
  pattern, and the new diff breaks that pattern, flag it.

## What NOT to flag

- Old code patterns being modernized (that's progress, not a
  re-introduction). Look for explicit "fix:" or "remove X because Y"
  framing in the prior commit before flagging a re-introduction.
- Changes to code that has churned a lot with no clear stated intent in
  commit messages (no signal to consider violated).
- Style/formatting differences from history.
- General code quality (other lenses' jobs).
- Stale commits older than a year, unless they're explicitly marked as
  invariant ("never X — security").`,
    calibration: `The scoring agent will filter on confidence ≥ 80 — flag only cases where
the historical evidence is clear and the contradiction is direct.`,
  },
  "lens-4-past-prs": {
    body: `You are **Lens 4** of a six-lens pre-flight code review circus. Your job
is to surface review concerns from prior PRs on the same files that may
apply to the current change.

## Range to review

- Base SHA: \`{BASE}\`
- Head SHA: \`{HEAD}\`
- Repo: \`{REPO}\`
- Modified files: \`{MODIFIED}\`

## How to find prior PRs

\`{MODIFIED}\` is a convenience copy of the file list, not the authority on
it — it is caller-supplied and can arrive truncated or hand-trimmed.
\`{BASE}\` and \`{HEAD}\` already determine the list exactly, so derive your
own and iterate over that:

\`\`\`bash
git diff --name-only {BASE}..{HEAD}
\`\`\`

For each file in that derived list:

\`\`\`bash
gh search prs --repo {REPO} 'in:files <path>' --limit 10 --state closed \\
  --json number,title,url
\`\`\`

For each returned PR (closed and merged, prefer recent), read its review
comments:

\`\`\`bash
gh api repos/{REPO}/pulls/<N>/comments       # inline review comments
gh api repos/{REPO}/pulls/<N>/reviews        # formal reviews
gh api repos/{REPO}/issues/<N>/comments      # general PR thread comments
\`\`\`

Skim each for review concerns. You can stop once you've covered the 5-10
most recent PRs per file; ancient PRs rarely carry applicable context.

## What to flag

- **Prior reviewer concerns that apply to the current change.** Example:
  reviewer on PR #45 said "this function shouldn't catch bare \`Exception\`
  — narrow it". The current diff again catches bare \`Exception\` in the
  same region → flag with a link to the prior comment.
- **Conventions agreed in prior review threads.** If a prior PR's review
  thread settled "we name these variables X, not Y", and the new diff
  uses Y, flag it.
- **Bugs caught and fixed in prior PRs** that the current diff appears
  to re-introduce, where the concern was raised in the *review* (not
  just the commit — lens 3 covers commit-message intent).
- **Architectural decisions documented in PR descriptions or threads**
  that the current diff contradicts.

## What NOT to flag

- Reviewer concerns specific to a different change context (e.g. "this
  was wrong in PR #45 because of the migration, but the migration is
  long over").
- General code-quality opinions from individual reviewers without
  consensus or follow-through.
- Concerns already addressed in CLAUDE.md (lens 1's job).
- Reviewer concerns on lines the current diff does not touch.`,
    calibration: `The scoring agent will filter on confidence ≥ 80 — flag only where the
prior reviewer's concern is clearly still applicable to the current
change context, not just superficially related.`,
  },
  "lens-5-code-comments": {
    body: `You are **Lens 5** of a six-lens pre-flight code review circus. Your job
is to read inline comments and docstrings in the **full files** at HEAD
and flag changes that contradict guidance written adjacent to the code.

This lens is **not** diff-only. Read each modified file in full at HEAD —
via \`git show {HEAD}:<path>\`, not the working tree — to see comments that
may live outside the hunks but constrain the hunks' behavior.

## Range to review

- Base SHA: \`{BASE}\`
- Head SHA: \`{HEAD}\`
- Modified files: \`{MODIFIED}\`

\`\`\`bash
git diff {BASE}..{HEAD}
# For each modified file still present at HEAD (skip files the diff
# deletes — {HEAD} has no content for them):
git show {HEAD}:<path>
\`\`\`

\`{MODIFIED}\` is a convenience copy of the file list, not the authority on
it — it is caller-supplied and can arrive truncated or hand-trimmed.
\`{BASE}\` and \`{HEAD}\` already determine the list exactly, so derive your
own and iterate over that:

\`\`\`bash
git diff --name-only {BASE}..{HEAD}
\`\`\`

## What to attend to in each file

Pay particular attention to:

- **Module-level docstrings** — top-of-file invariants and contracts.
- **Class-level docstrings** — invariants the class is supposed to
  maintain.
- **Function / method docstrings** adjacent to or covering changed lines.
- **Inline comments adjacent to changed lines** — \`±10\` lines from any
  diff hunk.
- **Comments with explicit warning markers** anywhere in the file:
  \`# NOTE:\`, \`# WARNING:\`, \`# INVARIANT:\`, \`# DO NOT\`, \`# TODO\` (if it
  warns about something the diff might trigger), \`# HACK:\`, \`# XXX:\`.
- **Sphinx / Google / NumPy style docstring sections** that document
  Raises, Returns, Yields, Postconditions.

## What to flag

- **Diff contradicts an adjacent comment.** Example: comment says \`# this
  list must be sorted for binary search below\` and the diff removes the
  sort.
- **Diff violates a documented invariant.** Example: docstring says
  "raises ValueError if input is empty" and the diff returns silently
  for empty input.
- **Diff changes behavior described in a docstring without updating the
  docstring** (docstring rot). Example: docstring says "returns the
  first match" and the diff makes it return all matches.
- **Diff adds new code in a region with a comment that the new code
  violates.** Example: comment says \`# allocations in this function are
  hot path — avoid\` and the diff adds a list comprehension that
  allocates.
- **Diff modifies a function whose docstring promises certain
  side-effects** (e.g. "this also writes to the audit log") and the diff
  removes those side-effects.

## What NOT to flag

- Comments that document the obvious "what" (e.g. \`# loop over items\`)
  rather than a "why" or invariant.
- Comments in unchanged regions of the file that have no causal relation
  to the diff.
- Stylistic comment disagreement (comment is poorly worded but
  semantically OK).
- Issues other lenses cover (CLAUDE.md rules → lens 1; obvious bugs →
  lens 2; etc.).
- Docstrings that are clearly stale and known-broken (some codebases let
  these accumulate; flag only if the diff makes the staleness *worse* or
  if the staleness would mislead someone reading the function after this
  change).`,
    calibration: `The scoring agent will filter on confidence ≥ 80 — flag only where the
contradiction is direct (not a loose interpretation), and where the
comment carries actual constraining force (not just casual prose).`,
  },
  "lens-6-normative-conformance": {
    body: `You are **Lens 6** of a six-lens pre-flight code review circus. Your job is to
review the change the way a standards body reviews a draft: every normative
statement must be **testable**, correctly **keyworded**, **complete**, and
**unambiguous**, and where a formal artifact backs a claim you **construct an
instance and execute it** rather than reasoning about the outcome.

## Range to review

- Base SHA: \`{BASE}\`
- Head SHA: \`{HEAD}\`
- Modified files: \`{MODIFIED}\`

\`\`\`bash
git diff {BASE}..{HEAD}
# then, for each modified normative file still present at HEAD (skip
# files the diff deletes — {HEAD} has no content for them):
git show {HEAD}:<path>
\`\`\`

\`{MODIFIED}\` is a convenience copy of the file list, not the authority on
it — it is caller-supplied and can arrive truncated or hand-trimmed.
\`{BASE}\` and \`{HEAD}\` already determine the list exactly, so derive your
own and iterate over that. This matters most for the applicability
self-check below: a short list is how you would wrongly conclude the range
contains no normative content.

\`\`\`bash
git diff --name-only {BASE}..{HEAD}
\`\`\`

## When this lens applies — self-check first

This lens dispatches unconditionally on every diff, whether or not it
touches normative-standard content — confirm applicability yourself.
Concluding this range contains none is a correct, expected outcome on
most runs, not a sign something went wrong. A modified file is in scope
if it is either:

- **(a) a formal schema or interface contract** — JSON Schema, OpenAPI/Swagger,
  \`.proto\`, XSD, Avro, or a TypeScript/IDL file declared as a wire or protocol
  schema; or
- **(b) a prose document that imposes conformance requirements on independent
  implementations** — it uses RFC-2119 \`MUST\`/\`SHALL\`/\`SHOULD\`/\`REQUIRED\`
  language normatively, defines an on-the-wire format or protocol, or otherwise
  states requirements another party must implement against (a format/protocol
  standard, an RFC/SEP-style document).

Not in scope: design docs, ADRs, explainers, tutorials, READMEs — informative
prose that *describes* a design without *imposing* conformance — even when they
sit under a \`spec/\` directory. Path is not the signal; normative content is.

If none of the modified files are normative-standard content, report
**"No normative-standard content in this change; lens not applicable."** and
stop.

## What to check

Review only the normative statements the diff **adds or changes** (plus any
untouched section a new claim depends on for its truth — you must read that
section to verify the new claim).

### 1. Testability — the load-bearing check

Enumerate every normative statement in the diff: each \`MUST\`/\`MUST NOT\`/\`SHALL\`/
\`SHALL NOT\`/\`SHOULD\`/\`SHOULD NOT\`/\`REQUIRED\`, and every declarative normative
promise written without a keyword ("the set is open", "a consumer validates the
message", "the endpoint rejects X"). For each, ask: **could an independent party
devise a conformance test for it?** If not, the statement is unverifiable — that
is defective normative language (the IETF rule: if no conformance test can be
devised, RFC-2119 keywords do not belong).

**Where a formal artifact backs the statement** (a JSON Schema, a type, an
example), do not stop at "a test could be devised." You have \`Bash\`, \`Read\`,
\`Write\` — use them:

- Construct the concrete instance the statement *predicts* should be accepted,
  and the **adversarial instance** that would be accepted/rejected *only if the
  statement were false*.
- Actually run the check: materialize the whole tree at HEAD to a scratch
  directory first — \`git archive {HEAD} | tar -x -C "$dir"\` — rather than
  copying the single file, so relative references (\`$ref\`, imports,
  \`tsconfig.json\`) still resolve; then validate the instance against
  \`$dir/<path>\` (a JSON Schema 2020-12 validator — \`python3\` +
  \`jsonschema\`, or \`npx ajv\`), compile the type (\`npx tsc\`), etc.
- Report every statement whose **executed result contradicts its prose**.

This is the step that catches "the spec promises a later message validates, but
the schema's \`oneOf\` rejects it." Observe the outcome; do not predict it. If no
checker is available in the environment, trace the artifact's behavior by hand
and say explicitly that the finding is unverified-by-execution.

### 2. Normative-keyword discipline

\`MUST\` is reserved for requirements whose violation breaks **interoperability,
safety, security, or data integrity**. \`SHOULD\` is for strong recommendations
that permit a justified deviation. Flag:

- \`MUST\` on something untestable (overlaps check 1).
- RFC-2119 keywords used in clearly informative/explanatory prose.
- A requirement whose violation *would* break interoperability/safety/security/
  data integrity but is stated as \`SHOULD\` — or the reverse, a soft preference
  stated as \`MUST\`.
- Normative force asserted by a plain declarative sentence in a document that
  otherwise uses keywords (an implementer cannot tell if it binds).

### 3. Completeness

Every behavior, state, case, and error path the standard *implies* must be
specified. Flag implied-but-unspecified behavior, undefined error or edge
cases, and operations whose outcome is not stated. For a **universally
quantified** claim ("every object", "all transports", "the set is open"),
**enumerate the domain and confirm each member is actually covered** — a gap in
the domain is an incompleteness, and this is exactly how an over-broad claim is
caught.

### 4. Unambiguity / interoperability

The objective of a standard is interoperable independent implementations. For
each normative statement, ask: **could two competent implementers read this and
build non-interoperable things?** Flag any statement admitting more than one
reasonable reading, any term used normatively without a definition, and any
on-the-wire format or processing step left underspecified.

## What NOT to flag

- Pure prose quality, wording, or style.
- A plain contradiction between two pieces of *text* — that is lens 5's job.
  You flag a claim contradicted by an artifact's executed behavior, or a
  statement that is untestable / incomplete / ambiguous / mis-keyworded.
- Issues in explicitly informative (non-normative) sections — unless the
  informative text would mislead an implementer about a normative requirement.
- Design opinions ("I would architect this differently").
- Pre-existing normative statements on lines the diff did not touch.`,
    calibration: `The scoring agent filters at confidence ≥ 80. An executed finding (you ran the
instance and the result contradicts the prose) is high-confidence — report it
plainly. A testability/keyword/ambiguity finding with no executed check should
be reported only where an independent implementer would genuinely be misled or
a conformance test genuinely cannot be written.`,
  },
  "score-confidence": {
    body: `You are the **confidence-scoring agent** for the pre-flight review
circus. For each issue surfaced by a lens, return a 0-100 confidence
score using the rubric below. This is the same rubric the post-push
\`/code-review:code-review\` bot uses, by design.

## Issue under review

{ISSUE}

## Lens that surfaced it

{LENS}

## Rubric

- **0** — Not confident at all. False positive that doesn't stand up to
  light scrutiny, or a pre-existing issue on lines the diff didn't
  modify.
- **25** — Somewhat confident. Might be real, might be false positive.
  You cannot verify. If stylistic, not explicitly called out in
  CLAUDE.md.
- **50** — Moderately confident. Verified real, but might be a nitpick or
  rare in practice. Not very important relative to the rest of the diff.
- **75** — Highly confident. You double-checked. Likely real, likely hit
  in practice, the existing approach is insufficient. Important and
  impacts functionality, OR directly mentioned in CLAUDE.md as an
  explicit rule.
- **100** — Absolutely certain. Double-checked and confirmed real, will
  happen frequently in practice. Evidence directly confirms.

## Verification before scoring

- For **CLAUDE.md-flagged issues** (lens 1), double-check the CLAUDE.md
  file actually calls out the specific issue. If the rule cited is
  vague or only superficially related, score ≤ 25.
- For **diff-flagged issues** (lens 2), verify the bug is actually
  visible in the current diff state, not just speculation. If the
  surrounding context (which lens 2 didn't read) would make this a
  non-bug, score ≤ 25.
- For **history / past-PR issues** (lenses 3 and 4), verify the cited
  prior context is real, recent, and applicable to the current change.
  Old context, or context from a different domain in the same file,
  scores ≤ 25.
- For **comment-contradiction issues** (lens 5), verify the comment
  actually carries constraining force (not casual prose), and the
  contradiction is direct.
- For **normative-conformance issues** (lens 6): if the lens ran an
  executable check (validated an instance against a schema, compiled a
  type) and the executed result contradicts the prose, trust it — score
  high. For testability, ambiguity, or keyword-discipline findings with
  no executed check, score ≥ 80 only where an independent implementer
  would genuinely be misled or a conformance test genuinely cannot be
  written. Prose-style nitpicks, and findings in explicitly informative
  (non-normative) sections, score ≤ 25.

## Common false-positive patterns (drop to score 0-25)

- Pre-existing issues on lines the diff did not modify.
- Something that looks like a bug but is idiomatic / intentional in this
  codebase.
- Pedantic nitpicks a senior engineer wouldn't call out in a PR review.
- Issues a linter, typechecker, or CI would catch (formatting, import
  order, pedantic style, type errors caught by mypy / tsc, unused
  imports).
- General code-quality opinions not codified in CLAUDE.md (poor naming,
  lack of abstraction, "this could be more functional", etc.).
- Issues flagged in CLAUDE.md but silenced in the code by intent (e.g.
  \`# noqa\` or \`# type: ignore\` with an explanatory comment).
- Intentional changes clearly related to the broader stated goal of the
  PR.
- Real issues on lines the user did not modify in the diff.`,
    calibration: ``,
  },
}


function fill(tpl, vars) {
  let out = tpl
  for (const [k, v] of Object.entries(vars)) {
    out = out.split('{' + k + '}').join(String(v))
  }
  return out
}

// `status` describes what happened; `verdict` prescribes what you may do
// about it. Both are derived from values this script already holds — no
// schema field, no prompt change, nothing asked of any agent.
//
// The blocked case reads `status` rather than re-testing
// `coreErrors`/`unscored`/`degraded`, so the three channels that gate
// `status` — a core lens that did not run, a finding whose scorer died, and a
// core lens reporting `examined: 'none'` — reach `blocked` by composition. A
// fourth channel added to that gate later becomes `blocked` for free instead
// of needing a second copy of the rule here. `degraded: 'partial'`
// deliberately does not gate `status`, and so deliberately does not block
// `clear`: a machine permanently missing an optional validator would
// otherwise never reach `clear`, and an alarm that always fires trains the
// operator to ignore it. `partial` stays separately visible in `degraded`.
//
// The surviving-findings thresholds live here and nowhere else. SKILL.md used
// to restate the number in prose and now defers to these names, because a
// threshold kept in two places drifts.
//
// Declared above the args validation below because both exits — that abort
// and the completed run at the bottom — return a verdict, so every exit
// carries one consistent shape.
const VERDICTS = {
  blocked: {
    name: 'blocked',
    directive:
      'The run did not complete. Fix the invocation or the environment and run it again. Do not triage: there is nothing here to act on, and the findings list is not evidence of anything either way.',
  },
  clear: {
    name: 'clear',
    directive: 'Push.',
  },
  'fix-and-rerun': {
    name: 'fix-and-rerun',
    directive:
      'Fix each surviving finding, or write its one-line defense, then re-run the full circus against the new range.',
  },
  structural: {
    name: 'structural',
    directive:
      'STOP. Fixing these and re-running is FORBIDDEN. A list this long is itself the finding, not a workload: patching your way down it is the linter behavior this gate exists to refuse, and every fix makes the next round cheaper to rationalize. Diagnose why the list is long before you touch a single finding, and expect to restart from a clean state rather than continue on this one.',
  },
}

// Count-based and round-agnostic, deliberately: the script is stateless and
// cannot know which round this is. Four findings on round two is, if
// anything, more structural than four on round one.
function verdictFor(runStatus, survivingCount) {
  if (runStatus === 'error') return VERDICTS.blocked
  if (survivingCount === 0) return VERDICTS.clear
  if (survivingCount <= 3) return VERDICTS['fix-and-rerun']
  return VERDICTS.structural
}

// The runtime types promise args as a {base, head, repo, modified} object,
// but empirically the harness hands it over JSON-encoded (one string), so
// this parse is load-bearing rather than defensive. Without it args.base
// etc. are all undefined, fill() happily stringifies undefined, and every
// lens reviews the range "undefined..undefined" and reports no findings: a
// clean bill of health for a review that never ran.
let rawArgs = args
if (typeof rawArgs === 'string') {
  try {
    rawArgs = JSON.parse(rawArgs)
  } catch {
    rawArgs = {}
  }
}
rawArgs = rawArgs && typeof rawArgs === 'object' ? rawArgs : {}

// Presence alone is not enough. A caller following SKILL.md by hand can
// paste the placeholder names through instead of substituting them, and
// the literal strings "BASE"/"HEAD"/"$BASE" are all non-empty — every lens
// would then run `git diff BASE..HEAD`, get `fatal: ambiguous argument`,
// and return an empty findings array per the output spec: 'clean' with
// eleven lenses "run" and zero errors. Validate the shape the producing
// command guarantees. This costs zero agents.
const REQUIRED_ARG_KEYS = ['base', 'head', 'repo', 'modified']
const ARG_SHAPES = {
  base: {
    ok: (v) => /^[0-9a-fA-F]{7,40}$/.test(v),
    expected: 'a 7-40 character hex commit SHA, as produced by `git merge-base`',
  },
  head: {
    ok: (v) => /^[0-9a-fA-F]{7,40}$/.test(v),
    expected: 'a 7-40 character hex commit SHA, as produced by `git rev-parse HEAD`',
  },
  repo: {
    ok: (v) => /^[^\s/]+\/[^\s/]+$/.test(v),
    expected: 'owner/name, as produced by `gh repo view --json nameWithOwner`',
  },
  // `modified` is a newline-separated path list; non-empty is the only
  // shape there is to check.
}

const argProblems = []
for (const k of REQUIRED_ARG_KEYS) {
  const v = rawArgs[k]
  if (typeof v !== 'string' || v.length === 0) {
    argProblems.push(`${k}: missing or empty`)
    continue
  }
  const shape = ARG_SHAPES[k]
  if (shape && !shape.ok(v)) {
    argProblems.push(`${k}: got ${JSON.stringify(v)}, expected ${shape.expected}`)
  }
}

if (argProblems.length) {
  // The offending keys and their expected shapes are the actionable part;
  // the abort deliberately does not speculate about *why* they are wrong.
  const reason = `invalid args — ${argProblems.join('; ')}`
  log(`ABORT: ${reason}`)
  const abortVerdict = verdictFor('error', 0)
  log(`verdict: ${abortVerdict.name} — ${abortVerdict.directive}`)
  return {
    status: 'error',
    verdict: abortVerdict,
    lensesRun: [],
    lensesSkipped: [],
    coreErrors: [{ id: 'args', reason }],
    // The abort path emits the same nine fields as a completed run, so a
    // caller never has to branch on which shape it got back.
    degraded: [],
    rawCounts: {},
    surviving: [],
    unscored: [],
  }
}

const VARS = {
  BASE: rawArgs.base,
  HEAD: rawArgs.head,
  REPO: rawArgs.repo,
  MODIFIED: rawArgs.modified,
}

const FINDINGS_SCHEMA = {
  type: 'object',
  required: ['findings', 'coverage'],
  properties: {
    coverage: {
      type: 'object',
      required: ['examined', 'blockers'],
      description:
        'Whether this lens was able to carry out its procedure over the range',
      properties: {
        examined: {
          type: 'string',
          enum: ['full', 'partial', 'none'],
          description:
            "'full' = ran the whole procedure; 'partial' = something stopped part of it and a real conclusion was still reached on the rest; 'none' = reached no conclusion, so the findings array carries no information",
        },
        blockers: {
          type: 'array',
          description:
            'One entry per obstacle. Empty only when examined is full.',
          items: {
            type: 'object',
            required: ['what', 'why'],
            properties: {
              what: {
                type: 'string',
                description: 'The capability, command, or access that failed',
              },
              why: {
                type: 'string',
                description: 'The observed failure — exit status, error text, or reason it was unusable',
              },
            },
          },
        },
      },
    },
    findings: {
      type: 'array',
      items: {
        type: 'object',
        required: ['file', 'summary', 'evidence'],
        properties: {
          file: { type: 'string', description: 'Repo-relative path' },
          line: { type: 'integer', description: '1-indexed line, omit if not line-specific' },
          summary: { type: 'string', description: 'One sentence stating the defect' },
          evidence: { type: 'string', description: 'Verbatim quote or citation supporting the finding' },
          suggestedFix: { type: 'string', description: 'Concrete change' },
        },
      },
    },
  },
}

const SCORE_SCHEMA = {
  type: 'object',
  required: ['score', 'justification'],
  properties: {
    score: { type: 'integer', minimum: 0, maximum: 100 },
    justification: { type: 'string' },
  },
}

const OUTPUT_SPEC = `

## Output

Report each issue through the StructuredOutput tool:

- \`file\` / \`line\` — where the issue is, in the new code.
- \`summary\` — one sentence stating what is wrong.
- \`evidence\` — the verbatim quote this lens rests on, with its own
  file:line where it has one: the CLAUDE.md rule, the diff line, the commit
  SHA and subject, the prior review comment and its URL, the comment or
  docstring, or the normative statement.
- \`suggestedFix\` — the concrete change.

If you find nothing, or this lens does not apply to the range, return an
empty findings array.

## Coverage

Also report \`coverage\` — one object for your whole review, not one per
finding. It records whether you were able to carry out your procedure at
all. It is not a self-assessment of how well you reviewed; it is an
observable fact about your tooling, on the order of "\`npx ajv\` exited 127".

- \`examined: "full"\` — you ran your whole procedure over the range. Set
  \`blockers\` to \`[]\`. **An empty findings array plus \`full\` is the normal,
  expected result**, and so is a lens whose specialization does not apply to
  this range: you examined it, it was not your business, that is \`full\` and
  not \`none\`.
- \`examined: "partial"\` — something stopped part of your procedure and you
  reached a real conclusion on the part you could reach. Say so whenever
  anything got in your way. This is a useful report rather than an admission
  of failure: it tells the operator which tool to install or which access to
  grant, and it does not block their push. Rounding a blocked step up to
  \`full\` is the single thing that makes this field worthless — a clean
  verdict from a check that never ran is exactly what it exists to catch.
- \`examined: "none"\` — you reached no conclusion, so your findings array
  carries no information. Reserve this for a procedure that did not
  meaningfully run: the repository state, credentials, or tools you depend on
  were absent, so you have nothing to report either way. It is not the answer
  for "I looked and found nothing".

\`blockers\` names what stopped you, one entry per obstacle:

- \`what\` — the capability, command, or access that failed, named precisely
  enough to act on (\`npx ajv\`, \`gh search prs\`, \`git log --follow\`).
- \`why\` — what you actually observed: the exit status, the error text, the
  reason it could not be used.

Anything other than \`full\` needs at least one blocker. Naming the obstacle is
the part the operator can act on; a bare \`partial\` with nothing behind it
cannot be fixed by anyone.`

const SCORE_OUTPUT_SPEC = `

## Output

Report through the StructuredOutput tool: \`score\` is the 0-100 value from
the rubric, \`justification\` is the one sentence.`

const CORE = [
  'lens-1-claude-md',
  'lens-2-shallow-diff',
  'lens-3-git-history',
  'lens-4-past-prs',
  'lens-5-code-comments',
  'lens-6-normative-conformance',
]

const SUPPLEMENTARY = [
  'pr-review-toolkit:code-reviewer',
  'pr-review-toolkit:silent-failure-hunter',
  'pr-review-toolkit:type-design-analyzer',
  'pr-review-toolkit:pr-test-analyzer',
  'pr-review-toolkit:comment-analyzer',
]

const SUPPLEMENTARY_PROMPT = `Review the changes in this repository between base commit {BASE} and head
commit {HEAD}.

Repository: {REPO}

Modified files (a caller-supplied convenience copy, which can arrive
truncated — derive the authoritative list yourself with
\`git diff --name-only {BASE}..{HEAD}\`):
{MODIFIED}

Review the full range \`{BASE}..{HEAD}\`, not the most recent commit alone.
Apply your own specialization to this range. If your specialization does not
apply to these changes, return an empty findings array.` + OUTPUT_SPEC

const skipped = []
const coreErrors = []
// Lenses that reported less than full coverage of the range. A fourth
// failure channel alongside coreErrors (a lens did not run), skipped (an
// agent would not dispatch) and unscored (a finding lost its scorer) — this
// one is for a lens that ran but could not see everything it needed to.
const degraded = []
const rawCounts = {}

const EXAMINED_VALUES = ['full', 'partial', 'none']

async function runLens(id, isCore) {
  const prompt = isCore
    ? fill(PROMPTS[id].body + OUTPUT_SPEC + '\n\n' + PROMPTS[id].calibration, VARS)
    : fill(SUPPLEMENTARY_PROMPT, VARS)

  const opts = {
    label: id,
    phase: 'Lenses',
    schema: FINDINGS_SCHEMA,
    // Pin the finders to sonnet rather than letting them inherit the session
    // model. The circus is a gate: it applies a fixed bar, and the prompts
    // below were written and calibrated against Claude models. Without this
    // pin the lenses would follow whatever model the operator happens to be
    // driving the session with (sonnet one day, a non-Anthropic model the
    // next), so the same diff would pass or fail on the luck of the session.
    // The gate's behaviour has to be a property of the gate, not of the
    // session. Scoring is pinned separately to haiku below — it is a cheap
    // mechanical confidence rating, not a judgement call.
    model: 'sonnet',
    // Every lens gets full tool access, and one of the supplementary agents
    // has previously run `git checkout main` in a shared working tree and
    // reverted the user's uncommitted work. isolation:'worktree' on ALL
    // eleven agents (core and supplementary alike) is the user's explicit
    // ruling to prevent that, made against the runtime's general guidance
    // toward a shared tree — do not remove it as an apparent mistake.
    // worktree.baseRef is set to 'head', so these worktrees carry branch
    // state rather than starting empty.
    isolation: 'worktree',
  }
  if (!isCore) opts.agentType = id

  let result = null
  let failure = null
  try {
    result = await agent(prompt, opts)
    if (!result) failure = 'agent returned null (terminal error or skipped)'
  } catch (e) {
    failure = String((e && e.message) || e)
  }

  if (failure) {
    if (isCore) {
      coreErrors.push({ id, reason: failure })
      log(`ERROR core lens ${id} did not run: ${failure}`)
    } else {
      skipped.push({ id, reason: failure })
      log(`skip ${id}: ${failure}`)
    }
    return null
  }

  // FINDINGS_SCHEMA requires `findings`, so the runtime's schema validation
  // should make a non-array `findings` unreachable. But every other
  // fallback in this file makes core-lens degradation loud, and silently
  // coercing a schema-violating core lens to zero findings would go the
  // other way — a quiet false "clean". Treat that case as a core failure;
  // a supplementary lens without a real specialization contract just gets
  // a logged skip.
  if (!Array.isArray(result.findings)) {
    const reason = 'result.findings was not an array (schema violation)'
    if (isCore) {
      coreErrors.push({ id, reason })
      log(`ERROR core lens ${id} did not run: ${reason}`)
      return null
    }
    skipped.push({ id, reason })
    log(`skip ${id}: ${reason}`)
    return null
  }

  // `coverage` is the lens reporting whether its own procedure could run —
  // an observable fact about its tooling, not a self-grade, which is why a
  // design otherwise built on distrusting prose promises accepts it. Missing
  // or non-object is the same class of contract violation as a non-array
  // `findings` above, and takes the same split: loud for a core lens, a
  // logged skip for a supplementary one.
  const rawCoverage = result.coverage
  if (!rawCoverage || typeof rawCoverage !== 'object' || Array.isArray(rawCoverage)) {
    const reason = 'result.coverage was missing or not an object (schema violation)'
    if (isCore) {
      coreErrors.push({ id, reason })
      log(`ERROR core lens ${id} did not run: ${reason}`)
      return null
    }
    skipped.push({ id, reason })
    log(`skip ${id}: ${reason}`)
    return null
  }

  // Past this point the report is salvageable, so normalize instead of
  // rejecting — forgiving about shape, never about silence. Three rules:
  //
  //   1. An `examined` outside the enum says nothing about whether the range
  //      was examined, so it cannot be read as `full` or as `partial`. It
  //      becomes `none`: we cannot tell what the lens meant, which makes its
  //      findings untrustworthy either way.
  //   2. Anything below `full` that names no blocker keeps the level it
  //      reported and gains a synthesized blocker recording that the lens
  //      did not say why. The synthesized entry repairs the missing
  //      explanation, never the level — downgrading an unexplained `none` to
  //      a non-gating `partial` would be forgiving about exactly the silence
  //      this field exists to catch, and an unexplained "I reached no
  //      conclusion" is the report to trust least, not most.
  //   3. A `full` that carries blockers contradicts itself. On the honest
  //      reading a lens listing things it could not do is `partial`, so it
  //      is recorded as `partial` with its blockers kept. That surfaces it
  //      in `degraded` — where a caller reading the result object will
  //      actually see it — without gating.
  let examined = EXAMINED_VALUES.includes(rawCoverage.examined) ? rawCoverage.examined : 'none'
  const blockers = (Array.isArray(rawCoverage.blockers) ? rawCoverage.blockers : [])
    .filter((b) => b && typeof b === 'object' && !Array.isArray(b))
    .map((b) => ({
      what: typeof b.what === 'string' && b.what ? b.what : 'unspecified',
      why: typeof b.why === 'string' && b.why ? b.why : 'unspecified',
    }))

  if (examined !== 'full' && blockers.length === 0) {
    blockers.push({
      what: 'unspecified',
      why: `lens reported examined ${JSON.stringify(rawCoverage.examined)} but named no blocker`,
    })
  }

  if (examined === 'full' && blockers.length) {
    log(
      `note ${id}: reported examined full alongside ${blockers.length} blocker(s); recorded as partial`,
    )
    examined = 'partial'
  }

  if (examined !== 'full') {
    degraded.push({ id, core: isCore, examined, blockers })
    log(
      `degraded ${id}: examined ${examined} — ` +
        blockers.map((b) => `${b.what}: ${b.why}`).join('; '),
    )
    // A lens that reached no conclusion has a meaningless findings array.
    // For a supplementary agent that is the same outcome as one that would
    // not dispatch at all, so it takes the existing non-gating `skipped`
    // channel. A core lens stays in `lensesRun` — it did report — and gates
    // through `degraded` instead.
    if (examined === 'none' && !isCore) {
      const reason = 'agent reported coverage examined: none'
      skipped.push({ id, reason })
      log(`skip ${id}: ${reason}`)
      return null
    }
  }

  const findings = result.findings
  rawCounts[id] = findings.length
  return { id, findings }
}

phase('Lenses')

const LENSES = [
  ...CORE.map((id) => ({ id, core: true })),
  ...SUPPLEMENTARY.map((id) => ({ id, core: false })),
]

const scored = await pipeline(
  LENSES,
  (lens) => runLens(lens.id, lens.core),
  // Belt-and-braces: the runtime breaks the pipeline chain when stage one
  // returns null, so this ternary's `: []` branch is never actually
  // reached for a failed lens — stage two simply never runs for it. Kept
  // explicit rather than assuming that behavior silently.
  (result, lens) =>
    result
      ? parallel(
          // Each thunk wraps its own construction (fill()) and its own await
          // in one try/catch, not just a `.then`/`.catch` tacked onto a
          // promise chain: a `.catch` only sees a rejected agent() call or a
          // throw inside `.then` — it never sees a *synchronous* throw from
          // fill() or agent() itself, thrown before any promise exists. A
          // synchronous throw there would make parallel() resolve the thunk
          // to null, and the retained filter(Boolean) below would delete the
          // finding with no trace. try/catch around the whole body closes
          // that gap.
          result.findings.map((f) => async () => {
            const scoreLabel = `score:${lens.id}`
            try {
              const s = await agent(
                fill(PROMPTS['score-confidence'].body + SCORE_OUTPUT_SPEC, {
                  ISSUE: `${f.file}${f.line != null ? ':' + f.line : ''} — ${f.summary}\n\nEvidence: ${f.evidence}${f.suggestedFix ? '\n\nSuggested fix: ' + f.suggestedFix : ''}`,
                  LENS: lens.id,
                }),
                {
                  label: scoreLabel,
                  phase: 'Score',
                  model: 'haiku',
                  effort: 'low',
                  schema: SCORE_SCHEMA,
                },
              )
              if (!s) {
                const reason = 'scoring agent returned null (terminal error or skipped)'
                log(`ERROR ${scoreLabel} did not score this finding: ${reason}`)
                return { ...f, lens: lens.id, score: null, justification: null, reason }
              }
              return { ...f, lens: lens.id, score: s.score, justification: s.justification }
            } catch (e) {
              const reason = String((e && e.message) || e)
              log(`ERROR ${scoreLabel} did not score this finding: ${reason}`)
              return { ...f, lens: lens.id, score: null, justification: null, reason }
            }
          }),
        )
      : [],
)

// Every degradation path elsewhere in this file is loud (ERROR/skip/ABORT
// log lines); a dead scorer is the one path that used to log nothing and
// discard its error. The try/catch above now always logs and carries a
// `reason` on the null-score sentinel it returns instead of collapsing the
// finding to nothing, so unscored findings surface with a cause instead of
// silently vanishing.
//
// The partition is `Number.isFinite`, not a null check: a scorer resolving
// truthy with a score of "n/a", false, or NaN is neither null nor >= 80,
// so a null-based partition drops it out of both buckets — a finding that
// vanishes into a 'clean' result. isFinite also keeps the sort below
// deterministic, since `b.score - a.score` on a non-numeric score is NaN.
// The sentinel is attached here rather than only at the two dead-scorer
// sites, so every `unscored` entry carries the {score, justification,
// reason} triple SKILL.md promises the caller — including entries that
// arrived with a truthy-but-unusable score and therefore have no `reason`
// of their own.
const flatScored = scored.flat().filter(Boolean)

const unscored = flatScored
  .filter((f) => !Number.isFinite(f.score))
  .map((f) => ({
    ...f,
    score: null,
    justification: null,
    reason:
      f.reason ||
      `scoring agent returned a non-numeric score (${typeof f.score}: ${String(f.score)})`,
  }))

const surviving = flatScored
  .filter((f) => Number.isFinite(f.score) && f.score >= CONFIDENCE_THRESHOLD)
  .sort((a, b) => b.score - a.score)

const lensesRun = [
  ...CORE.filter((id) => id in rawCounts),
  ...SUPPLEMENTARY.filter((id) => id in rawCounts),
]
// unscored findings mean "we don't know whether this was above the
// threshold" — that is not a clean bill of health, so it forces 'error'
// the same as coreErrors. coreErrors and unscored stay separate fields so
// the caller can still tell the two causes apart; only the status gate is
// shared.
//
// `degraded` gates on a narrower rule than the other three: only a core
// lens reporting `none`. An empty findings array from a lens that reached
// no conclusion is not evidence of anything, so that one must block. A
// `partial` deliberately does not: a machine permanently missing one
// optional checker would otherwise error on every run forever, and an alarm
// that always fires teaches the operator to skip it. `partial` stays in the
// result instead, so a lens running at half strength for a month is
// discoverable without blocking a push.
const gating = degraded.filter((d) => d.core && d.examined === 'none')
const status =
  coreErrors.length || unscored.length || gating.length
    ? 'error'
    : surviving.length
      ? 'findings'
      : 'clean'

const verdict = verdictFor(status, surviving.length)

log(
  `${lensesRun.length} lenses ran, ${skipped.length} skipped, ` +
    `${surviving.length} findings at >=${CONFIDENCE_THRESHOLD}, ${unscored.length} unscored, ` +
    `${degraded.length} degraded (${gating.length} gating)`,
)
log(`verdict: ${verdict.name} — ${verdict.directive}`)

return {
  status,
  verdict,
  lensesRun,
  lensesSkipped: skipped,
  coreErrors,
  degraded,
  rawCounts,
  surviving,
  unscored,
}
