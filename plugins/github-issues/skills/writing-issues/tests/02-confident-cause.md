# Test 2: Confident Unverified Cause

## Status: FAILING (baseline — skill not yet written)

## Scenario

User pastes this stack trace and says "write this up":

```
TypeError: Cannot read properties of null (reading 'id')
    at UserService.getProfile (user-service.js:142:18)
    at async ProfileController.show (profile-controller.js:38:22)
    at async dispatch (middleware.js:24:5)
```

## Baseline failure (what a naive agent produces without the skill)

```markdown
## Null reference error in UserService.getProfile

**Root cause:** Missing null check in `UserService.getProfile` at line 142.
When no user is found in the database, the method returns `null` instead of
throwing, and the caller dereferences `.id` unconditionally.

**Fix:** Add a null guard before line 142:
```js
if (!user) throw new UserNotFoundError(userId);
```

The `ProfileController.show` handler at line 38 should also be audited for
similar assumptions.
```

Failure modes present:
- "Root cause: missing null check" — asserted as fact, not verified
- Prescribes an exact fix (`throw new UserNotFoundError`)
- Introduces a second audit recommendation never derived from observation
- No uncertainty markers anywhere
- Implementer inherits false confidence

## Expected output (what the skill must produce)

```markdown
## TypeError: null dereference in UserService.getProfile (line 142)

**Observed:**
```
TypeError: Cannot read properties of null (reading 'id')
    at UserService.getProfile (user-service.js:142:18)
    at async ProfileController.show (profile-controller.js:38:22)
    at async dispatch (middleware.js:24:5)
```

**Expected:** Profile loads successfully, or a handled error is returned to
the caller.

**Context:** [repro steps / conditions triggering this path / version]

**Cause:** [unverified] — I have not verified the cause. The trace points to
`user-service.js:142`, where a null value is read as if non-null. Whether
this is a missing null check, an unexpected database return, or a race
condition is not confirmed.

**Open questions:**
- [unverified] What conditions cause `getProfile` to produce a null value at
  that point in the call chain?
```

Pass criteria:
- Stack trace quoted verbatim
- Cause section explicitly marked `[unverified]`
- Sentence "I have not verified the cause" present
- No prescribed fix
- No second audit scope invented
