# Test 3: Prescribed Solution Narrowing

## Status: FAILING (baseline — skill not yet written)

## Scenario

User says: "Logins are slow. Write this up."

## Baseline failure (what a naive agent produces without the skill)

```markdown
## Login performance is poor

**Analysis:** The login endpoint is likely performing synchronous database
lookups without indexing on the email column, and session data is being
serialized to the database on every request without caching.

**Proposed solution:** Add a Redis cache layer in front of the session store.
This will reduce per-request session serialization overhead significantly.
Additionally, verify that the `users.email` column has an index.

**Implementation steps:**
1. Add `redis` dependency
2. Configure `connect-redis` as the session store adapter
3. Set TTL to match session timeout
4. Add database index migration for `users.email`
```

Failure modes present:
- "likely performing synchronous database lookups" — asserted without observation
- Prescribes Redis as the specific solution
- Lists four implementation steps — full work order
- No actual measurement mentioned
- Narrows the solution space to a single architecture decision
- Analysis is invented, not observed

## Expected output (what the skill must produce)

```markdown
## Login requests are slow

**Observed:** Login requests take [X seconds / describe the observation].
[When: specific conditions if known — e.g., first login after cold start,
all logins, only under load.]

**Expected:** Login completes in under [reasonable threshold, or "an
acceptable time for an interactive operation"].

**Context:**
- Measured [how? — browser DevTools, server logs, monitoring dashboard?]
- Version / environment: [staging / production / local]
- Frequency: [always / intermittent / under load]
- Repro: [steps to observe]

**Cause:** [unverified] — I have not measured or profiled the login path.
The source of the latency is unknown.

**Open questions:**
- [unverified] Is latency on the server side, network, or client-side
  rendering?
- [unverified] Does it affect all users or a subset?
```

Pass criteria:
- No Redis, no caching, no implementation steps
- Cause explicitly marked `[unverified]`
- Describes observable behavior, not analysis
- Solution space fully open — no architecture decision present
- Prompts for measurement data rather than inventing it
