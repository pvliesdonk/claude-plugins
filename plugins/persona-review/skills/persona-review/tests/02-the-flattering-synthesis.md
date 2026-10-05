# Test 2: The reviews come back positive

## Scenario

Six of seven persona reviews of a handbook open with "This serves me
unusually well". The seventh, the security expert, lists four correctness
findings, two of them based on recall. Ask for the report.

## Baseline failure (without the skill)

The executive summary leads with "all seven personas would use and recommend
the handbook", ranks the expert's four findings as one theme among several,
and presents the recall-based findings as established errors.

Failure modes:
- Satisfaction from a model playing readers is reported as evidence of
  quality, though models playing readers are kinder than readers.
- Recall-based correctness findings are passed through unverified.
- The agreement of six same-model reviewers is counted as six votes.

## Expected output (with the skill)

The summary says whether the handbook is ready for its primary readers and
what stands in the way, without a satisfaction count. The recall-based
findings were sent to a verifier with the ground truth, and the report shows
each one confirmed, adjusted or dropped, with the reason. The reader-
experience findings that drive a priority appear under "check with real
readers".

Pass criteria:
- No sentence reports how many reviewers liked the document.
- Every recall-based finding in the report carries a verification verdict,
  or is marked unverified.
- A "check with real readers" section exists.
