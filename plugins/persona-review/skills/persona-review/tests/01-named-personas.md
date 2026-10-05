# Test 1: The user names the personas

## Scenario

User says: "Do a persona review of whitepaper.md with a CEO, a CFO and a COO.
Go."

## Baseline failure (without the skill)

Three reviewers are briefed with a job title each and asked for "critical but
constructive feedback". The three reviews raise the same points (add an
executive summary, quantify the benefits, shorten section 2) in three
voices, and the summary reports that "all three executives found the paper
compelling".

Failure modes:
- A job title is not a reader: no goal, entry point, budget or stop
  condition, so every reviewer reads the same way and finds the same things.
- No one asked whether a CFO and a COO would raise different findings.
- The paper's actual gatekeeper (whoever decides to buy) and its hostile
  reader are missing.
- Satisfaction is reported as a result.

## Expected output (with the skill)

Cards for the three named readers, each with what they came for and a mode
chosen for a white paper (read, since the question is whether it persuades;
a walk where a reader has a concrete task, such as "decide whether the
payback claim survives a budget meeting"). The distinctness test applied: if the CFO and COO would
raise the same findings, they are merged or one is sharpened. A proposal to
add an adversarial reader and, if the paper has one, the gatekeeper,
marked `assumed`. "Go" counts as permission to run without confirmation,
so the table is shown and the run starts.

Pass criteria:
- Every card has came_for and a mode; every walking card also has goal,
  entry, stop_when and budget_words.
- The distinctness test is visible in the confirmation table or the
  message.
- Any persona the user did not name is marked as added, with its source.
