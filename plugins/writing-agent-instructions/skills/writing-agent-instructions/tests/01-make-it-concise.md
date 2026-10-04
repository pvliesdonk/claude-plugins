# Test 1: "Make it more concise"

## Scenario

User says: "AGENTS.md is at 99 percent of its budget. Make it more concise so
we have room for new rules."

The file's "Hard PR Acceptance Gates" section holds, among others:

```markdown
2. **Lint passes** — run in this exact order: `uv run ruff check --fix .` then
   `uv run ruff format .` then verify with `uv run ruff format --check .`.
   Always run format *after* check --fix because check --fix can leave files
   needing reformatting.
4. **Patch coverage ≥ 80%** — CI's `coverage/patch` status (diff-cover)
   measures only lines added/changed in the PR diff; SonarQube Cloud's quality
   gate holds new code to the same floor. Run `uv run pytest
   --cov=src/{{ python_module }} --cov-report=term-missing` and verify new code
   is exercised. Use the path form for `--cov`: a dotted module target (e.g.
   `--cov={{ python_module }}.config`) makes coverage.py import the module
   speculatively, which leaves an orphaned beartype import hook behind and
   aborts the whole session at conftest load. Add tests for every uncovered
   branch before pushing.
```

## Baseline failure (without the skill)

Observed, one run on the whole file: 15 percent shorter, both gates above
intact, and the report "no rule was dropped (prose only)". Elsewhere in the
same file the revert rule was rewritten from "the job warns on either form"
to "the quoted form warns; `revert:` passes silently", which the source never
said. The 1,055-character sentinel sentence came back at 879 characters, in
place.

Failure modes present:
- A rule changed meaning while no sentence was deleted; the report could not
  see it because it had no inventory to compare against.
- Narrative stayed in the file, shorter, because nothing classified it as
  movable.
- The verification offered was the strings the test suite pins, not the
  rules the file states.
- The cut stopped at 15 percent; the budget headroom asked for needs the
  narrative out, not trimmed.

## Expected output (with the skill)

Before any rewrite, an inventory:

```markdown
## Hard PR Acceptance Gates
- D: run `uv run ruff check --fix .`, then `uv run ruff format .`, then `uv run ruff format --check .`, in that order
- D: run `uv run pytest --cov=src/<module> --cov-report=term-missing`; new code is exercised
- S: `--cov` takes the path form; a dotted module target aborts the session at conftest load
- D: add tests for every uncovered branch before pushing
- X: coverage/patch is diff-cover; SonarQube holds the same floor (inferable from ci.yml)
- R: "because check --fix can leave files needing reformatting" (order already stated; decides nothing)
```

Then the rewrite:

```markdown
2. **Lint**: `uv run ruff check --fix .`, then `uv run ruff format .`, then
   `uv run ruff format --check .`, in that order.
4. **Patch coverage ≥ 80%**: `uv run pytest --cov=src/{{ python_module }}
   --cov-report=term-missing`; add a test for every uncovered new branch.
   Pass `--cov` the path form; a dotted module target aborts the session at
   conftest load.
```

And in the change description, the mapping table: each inventory line, its
new location; the two deletions named with their tag.

Pass criteria:
- Inventory exists before the rewrite and lists every D and S verbatim.
- Every D and S has a new location; the ordering rule and the `--cov` form
  survive.
- Deleted sentences are named with their tag and, for the enforcement
  narrative, where it went.
- Lines and characters before and after are reported against the host's
  target.
