---
name: refactor-audit
description: Use when you need to find what to refactor across a Python codebase — surfacing technical debt, the worst or most complex code, god functions/classes, dead-code candidates, and an overall code-smell inventory, or establishing a refactoring baseline before a sprint. Triggers on requests to audit code quality, maintainability, or complexity at the codebase level. Not for fixing one already-identified file, debugging test/correctness failures, or non-Python code.
---

# Refactor-Audit

## Overview

Runs a fixed analyser set over a Python source tree, fuses the results with git
churn, and emits **one ranked triage shortlist** — instead of leaving a human to
run and reconcile half a dozen analysers by hand.

**Core principle — the hotspot model:** rank by `(churn or 1) * total_cc`.
Complexity alone says what is *ugly*; churn × complexity says what is ugly *and
changes often*, which is where refactoring pays. Everything else (maintainability
index, worst functions, smell inventory, dead code) **annotates** the ranking
rather than competing with it.

This is the **bootstrap** half: a one-shot scan before a refactor sprint, or to
seed a structural-health ratchet baseline. On-demand and repeatable, not literally
one-time. **Read-only — it identifies, it never edits.**

## When to use

- "What should I refactor first / where's the technical debt?"
- "Audit this codebase's quality / maintainability / complexity."
- "Find the worst / most-complex code, god functions, or dead code."
- "Establish a refactoring baseline before the sprint."

**Not for:** fixing a specific already-named file; debugging a failing test or a
correctness bug; non-Python codebases (the analyser set is Python-only).

## Running it

`radon` is the only hard dependency; every other analyser is skipped with a note
if absent. Inject them with `uv` so their console scripts are on PATH:

```bash
uv run --with radon --with lizard --with vulture --with ruff \
  python "${CLAUDE_PLUGIN_ROOT}/skills/refactor-audit/audit.py" <SOURCE_ROOT>
```

`<SOURCE_ROOT>` is the tree to scan; **cwd must be inside the target's git repo**
(it can be a parent of `<SOURCE_ROOT>`) so churn resolves. Outputs default to
`./refactor-audit.md` (triage report) and `./structural-baseline.json` (machine
seed); both `--md` and `--json` take a path to override:

```bash
uv run --with radon --with lizard --with vulture --with ruff \
  python "${CLAUDE_PLUGIN_ROOT}/skills/refactor-audit/audit.py" src/mypkg --md report.md --json baseline.json --churn-days 60
```

Other flags (sane defaults): `--churn-days 90`, `--top 15`, `--cc-threshold 10`,
`--vulture-min-confidence 60`, `--ruff-select`. Run `python
"${CLAUDE_PLUGIN_ROOT}/skills/refactor-audit/audit.py" --help` to list all flags
with their defaults.

The report sections, in order: **Top candidates** → **Worst functions** → **Smell
inventory** → **Dead-code candidates** → **What this does not catch**. A section is
absent only when its analyser was skipped (noted in the header) or found nothing.

The hotspot formula and the audit ruff selection are editable policy constants at
the top of `audit.py` (`hotspot_score`, `RUFF_AUDIT_SELECT`) — not buried.

## Reading the output

1. **Top candidates** rank by hotspot — start at rank 1.
2. **Worst functions** (lizard CCN) and **smell inventory** (ruff) tell you *what
   kind* of work each hotspot needs; they don't re-rank it.
3. The audit runs a **broad fixed ruff selection** independent of the project's own
   (often minimal, already-passing) config — signal completeness over low noise.
   It force-enables `PLR0904` (too-many-public-methods) because radon scores a
   class of many trivial methods as low complexity and misses god classes *by
   shape*.

**Why no manual churn de-noising:** decompositions/renames inflate raw churn, and
deleted files often top a naive churn list. Here churn only matters multiplied by
live complexity (`hotspot = churn × cc_total`), so a deleted or trivial file
scores ~0 and never ranks — the pollution cancels itself.

## What it does NOT catch

State this in any report you derive from it:

- **Semantic drift** — names and abstractions that no longer match behaviour. No
  metric sees this; it stays a human or agent-review job.
- **vulture (and cohesion) findings need confirmation.** vulture over-reports on
  importable / public-API code (decorated handlers, `__getattr__`, framework
  hooks look unused). It is ranked **triage input, not truth** — confirm before
  deleting and keep a whitelist.

A skill that oversells its coverage is worse than one that scopes itself.

## Seeding the ratchet (JSON contract)

`structural-baseline.json` carries per-file metrics — `cc_total`, `cc_max`, `mi`,
`loc`/`sloc`, `churn`, `hotspot`, and `worst_functions` — sorted by hotspot, plus
`smells`, `dead_code`, and `totals`. These measured values are the producer side
of the structural-health ratchet: the ratchet snapshots them as its initial
ceilings and tightens them over time. The continuous-gate (ratchet) half consumes
this file. If its expected key layout diverges, adapt the consumer or add a thin
transform — this script is the producer; the divergence point is documented here,
not silently bridged.

## Turning findings into issues

The audit is an **observation, not a work order.** When filing findings as tracker
issues, record *"this area is problematic and needs investigation"* — never a
prescribed refactor. One area per issue; cite the measured metrics and the commit
as the observation; mark any cause `[unverified]`; let the investigator decide
whether the complexity is essential or accidental. Use the writing-issues skill.

File an issue only when a finding marks a problematic area worth investigating:

- a **tier-1 hotspot** — top of the ranking, high on *both* churn and complexity;
- an **extreme complexity outlier** — a very high single-function CCN even where
  churn is low (a standalone risk the hotspot rank alone hides);
- a **structural smell** — e.g. a `PLR0904` god-class radon's per-block score misses.

Do **not** file for style smells the target already ignores under its own config,
for false-positive dead code (framework-registered handlers), or for single-line
cleanups. That discipline is what keeps the output a triage shortlist, not a
backlog dump.

## Optional analysers (not bundled — why)

- **wily** adds the *trend* axis (which files degrade across history) but its
  `wily build` step writes a `.wily/` cache, breaking the read-only guarantee — and
  it is low-maintenance (flagged inactive, no PyPI release in ~12 months as of late
  2025). Run it manually as a follow-up if you want trend.
- **cohesion** flags low-cohesion classes — a better god-class signal than method
  count (ruff has no too-many-instance-attributes rule). **grimp** lists import
  cycles. Both are niche and need per-project wiring, so they are manual add-ons,
  not part of the deterministic core.
