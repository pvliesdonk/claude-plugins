# Attested Computations (OKF v0.2 §10)

An Attested Computation concept carries not just what a value means but a sanctioned way to compute
it, so a consumer can confirm the agent ran the blessed computation instead of improvising its own.

Provenance answers "where did this claim come from". Attestation answers "was this number produced
the way we said it must be". OKF records the computation and the means to check it. It executes
nothing itself.

## One computation, one concept

A sanctioned computation is a standalone concept with `type: Attested Computation`. Concepts that
need the value (a `Metric`, a table concept, a report) link to it with an ordinary markdown link.

Three reasons it is standalone rather than a field on the consuming concept:

- `runtime` defines what `parameters` mean. A parameter is a SQL bind variable, a dbt var or a
  Python argument depending on the runtime, so keeping them in one frontmatter makes the binding
  semantics self-evident.
- One computation, many consumers. The same computation can back a metric, a dashboard concept and a
  report, referenced once and reused.
- Trust state is per computation. Revenue, profit and margin each verify and attest independently,
  which is three concepts, not three entries in one frontmatter. Revenue can be fresh while profit is
  past its `stale_after`.

## Contract fields

On top of the usual provenance, trust and lifecycle families:

- `runtime` — required for this type. Says how to run the computation and therefore how executor and
  attester interpret it and what `parameters` mean. Examples: `bigquery`, `postgres`, `dbt`,
  `python`, `Looker`.
- `parameters` — list of typed named holes the agent may fill, each `{ name, type, required }`.
- `computation` — optional path to a file holding the computation, used instead of an inline body
  fence. Absent means the body `# Computation` fence is the computation.
- `executor` — how the computation is run. `resource` names run instructions or code that a runner
  (an agent, or deterministic consumer code) follows. `receipt` declares the fields a run must
  return, which is the evidence the attester inspects, for example a BigQuery `job_id` and the SQL
  the job actually executed.
- `attester` — the deterministic check. `resource` names code with no LLM in it that takes a receipt
  and returns a verdict. Meant to run consumer-side.

What sits behind a `resource` (a skill, a script, a container) is a packaging choice. OKF fixes the
interface, not the packaging.

```yaml
---
type: Attested Computation
title: Revenue for fiscal year
description: Recognized revenue for a fiscal year, per Finance's definition.
status: stable
runtime: bigquery
parameters:
  - { name: year, type: integer, required: true }
executor:
  resource: references/skills/run-on-bq.md
  receipt: [job_id, executed_sql, result]
attester:
  resource: references/attesters/revenue.py
generated: { by: reference_agent/gemini-2.5-pro, at: 2026-06-20T22:53:05Z }
verified: { by: human:ahormati, at: 2026-06-25T09:00:00Z }
stale_after: 2026-09-23
sources:
  - id: rev-policy
    resource: https://wiki.acme/finance/revenue-recognition
    title: Revenue recognition policy
---
```

Body, with the computation inline:

```markdown
# Computation

    SELECT SUM(amount) AS revenue
    FROM finance.recognized_revenue
    WHERE fiscal_year = @year

The computation binds only the declared `parameters`, per the recognition policy.[^rev-policy]

[^rev-policy]: Revenue recognition policy
```

## Inline or file

- Inline: a single fenced code block under `# Computation`. Best for a short computation reviewed
  alongside its contract.
- File: set `computation` to a path and omit the body fence. Best for a long or generated
  computation, or one already kept as a real file shared with non-OKF tooling.

The agent may supply only values for the declared parameters. It must not author or edit the
computation. Binding the computation with parameter values into the executable artefact is the
consumer's job, and the attester independently re-derives that same binding to compare against what
actually ran. Because the comparison is against the expanded, compiled artefact the receipt carries
(`executed_sql`, `compiled_sql`), a rewritten query, a swapped computation file or a mutated
dependency fails the check. A typed, parameter-only surface is what turns "did the sanctioned thing
run" into a mechanical comparison rather than a judgement call.

## Consumer flow

Informative, not normative. The runtime artefacts here are not stored in the bundle.

1. **Discover** via `type: Attested Computation`, reachable directly or by following a link from a
   concept that uses it.
2. **Load** the contract from frontmatter and the computation from the body or the `computation`
   file.
3. **Parameterise**: supply values for the declared parameters, nothing else.
4. **Execute**: the executor runs the bound computation and returns a receipt shaped by
   `executor.receipt`.
5. **Attest**: run the attester over the receipt. It confirms provenance (what ran equals
   `computation` bound with the claimed parameters, not agent-authored SQL) and fidelity (the
   displayed value matches the receipt's authoritative source, re-read by job id rather than taken
   from the agent's text).
6. **Gate**: refuse to display a failing attestation; warn or refuse when `today >= stale_after`. On
   success, surface the verdict, for example a link to the job log, so trust is visible.

## Verification versus attestation

Both exist and they are not substitutes.

| | `verified` | Attestation |
| --- | --- | --- |
| Confirms | the definition still matches policy | a single run produced the value the sanctioned way |
| Granularity | document level | per call |
| Cadence | slow | every run |
| Stored | in the bundle | never; runtime only |

A concept with a stale definition can still attest cleanly, and a freshly verified definition still
requires attestation on each run.

## Bundle layout for a worked example

```
bundles/finance/
  metrics/income-statement.md      # type: Metric, narrates and links both figures
  computations/revenue.md          # type: Attested Computation, runtime: bigquery
  computations/profit.md           # type: Attested Computation, runtime: dbt
  references/skills/run-on-bq.md, run-dbt.md
  references/attesters/sql-equality.py, dbt-binding.py
```

The narrative concept carries no computation of its own. Trust lives on what it links to, so one
consumer reading one document can reach two different verdicts when one figure is fresh and the
other is past its `stale_after`.
