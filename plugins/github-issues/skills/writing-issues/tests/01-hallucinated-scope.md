# Test 1: Hallucinated Scope

## Status: FAILING (baseline — skill not yet written)

## Scenario

User says: "The export button does nothing when the list is empty."

## Baseline failure (what a naive agent produces without the skill)

```markdown
## Bug: Export button unresponsive on empty list

**Summary:** The export button does nothing when the list is empty. The import
handler likely shares this code path and is probably similarly broken. The
event handler should be refactored to guard against empty state uniformly
across both operations.

**Root cause:** Missing empty-state guard in the export handler. The same
pattern likely exists in the import handler.

**Proposed fix:** Refactor the shared handler to check `list.length > 0`
before dispatching, and add the same guard to the import path.
```

Failure modes present:
- Asserts "import is probably similarly broken" — never observed, invented
- "likely shares this code path" — stated as near-fact, unverified
- Proposes a refactor the user never asked for
- Narrows the solution space ("check `list.length > 0`")
- Two problems bundled (export + import) when only one was reported

## Expected output (what the skill must produce)

```markdown
## Export button unresponsive when list is empty

**Observed:** Clicking Export when the document list is empty produces no
visible response — no error, no dialog, no network request.

**Expected:** Either an export is initiated, or a clear error message is
shown explaining that there is nothing to export.

**Context:** [repro steps / version / commit if available]

**Open questions:**
- [unverified] Import may share this code path; not verified.
```

Pass criteria:
- Exactly one problem (export only)
- Adjacent suspicion is ONE LINE under open questions, marked `[unverified]`
- No proposed solution or refactor
- No cause asserted
