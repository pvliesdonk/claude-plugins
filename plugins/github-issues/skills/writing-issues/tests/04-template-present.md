# Test 4: Template Present

## Status: FAILING (baseline — skill not yet written)

## Scenario

User says: "Write up a bug — the save button hangs after network errors."

Repo has `.github/ISSUE_TEMPLATE/bug_report.yml` with these fields:
```yaml
- type: textarea
  id: describe-bug
  attributes:
    label: Describe the bug
- type: textarea
  id: to-reproduce
  attributes:
    label: To Reproduce
- type: textarea
  id: expected-behavior
  attributes:
    label: Expected behavior
- type: input
  id: version
  attributes:
    label: Version
```

## Baseline failure (what a naive agent produces without the skill)

```markdown
## Save button hangs after network error

**Describe the bug:** After a network error, the save button becomes
unresponsive and the UI enters an inconsistent state.

**To Reproduce:**
1. Open a document
2. Disconnect network
3. Press Save

**Expected behavior:** Save should retry or display an error message.

**Version:** unknown

**Root cause analysis:** The promise rejection from the network call is
not being caught, leaving the button in a loading state indefinitely.

**Proposed fix:** Wrap the save handler in a try/catch and reset button
state in the catch block.

**Additional context:** This may also affect the auto-save feature, which
uses the same underlying save function. The debounce timer may need to be
reset on error as well.
```

Failure modes present:
- Added "Root cause analysis" — field not in the template
- Added "Proposed fix" — field not in the template
- Added "Additional context" — field not in the template
- Invented scope ("auto-save", "debounce timer") never mentioned by user
- Asserted cause ("promise rejection not caught") without verification

## Expected output (what the skill must produce)

First, detect the template:
```bash
ls .github/ISSUE_TEMPLATE/
# → bug_report.yml
```
State: "Using bug_report.yml (only template present; matches bug kind)."

Then fill exactly the template's four fields:

```markdown
## Save button hangs after network error

**Describe the bug:** After a network error occurs during save, the save
button becomes unresponsive. The UI shows no error message and the button
does not recover.

**To Reproduce:**
1. Open a document
2. Trigger a network error (e.g., disconnect or block the request)
3. Click Save
4. Observe: button does not recover; no error displayed

**Expected behavior:** Either the save retries, or an error message is
shown and the button returns to its default state.

**Version:** [to be filled]
```

Pass criteria:
- Template was detected before writing
- Exactly four fields filled — no extras invented
- No cause, no fix, no proposed approach
- No adjacent speculation (auto-save, debounce)
- States which template was chosen
