# Test 3: A hedged rule

## Scenario

User says: "Add to CLAUDE.md: prefer running single tests where possible
rather than the whole suite, it's faster. Generally run the full suite before
pushing though."

## Baseline failure (without the skill)

Constructed from the request's own wording; not yet observed in a run:

```markdown
- Prefer running single tests where possible rather than the whole test
  suite, for performance. Generally run the full suite before pushing.
```

Failure modes present:
- `prefer`, `where possible` and `generally` leave the agent to decide what
  "possible" means; on a literal reader this is either always or never.
- "for performance" is a rationale that decides no case.
- No scope: single test of what, selected how.

## Expected output (with the skill)

```markdown
- While iterating, run the one test file or test id that covers the change
  (`uv run pytest tests/test_x.py::test_y`). Run the whole suite once before
  you push.
```

Pass criteria:
- No `prefer`, `consider`, `generally` or `where possible`; the condition is
  stated (while iterating; before you push).
- The command form is given once.
- No emphasis added; the rationale is dropped.
