---
name: open-knowledge-format
description: Author, validate, migrate and consume Open Knowledge Format (OKF) bundles, Google Cloud's vendor-neutral spec (v0.2) for agent-readable knowledge as markdown with YAML frontmatter. Use whenever OKF, "knowledge bundle", okf_version or "LLM wiki" comes up; when writing or generating markdown-plus-frontmatter knowledge for AI agents to consume; when turning a repo, wiki, Obsidian vault, data catalogue or schema into something agents can read; when checking conformance of concepts, index.md/log.md, or the type/sources/generated/verified/status/stale_after frontmatter families; when working with Attested Computation contracts, executors, attesters or receipts; and when migrating a v0.1 bundle to v0.2. Also use when someone asks whether their agent-knowledge folder follows the standard, or compares it with AGENTS.md, CLAUDE.md, llms.txt or RAG pipelines. Not for the Open Knowledge Foundation (okfn.org), an unrelated non-profit sharing the abbreviation.
---

# Open Knowledge Format (OKF)

OKF represents knowledge as a directory of markdown files with YAML frontmatter. No SDK, no schema
registry, no runtime. A conformant bundle is readable with `cat` and shippable with `git clone`.

Published by Google Cloud's Data Cloud team in the `GoogleCloudPlatform/knowledge-catalog` repo
(`okf/SPEC.md`, Apache 2.0). v0.1 landed 12-13 June 2026, v0.2 on 25 July 2026. It is explicitly an
early-stage spec, not a ratified standard, and its authors describe it as a starting point.

State this honestly when relevant: OKF fixes structural interoperability (a folder layout, two
reserved filenames, one required field, a handful of optional trust fields). It does not fix
semantic interoperability. There is no registry of `type` values, so two producers can describe the
same thing incompatibly and both remain conformant. Adoption outside Google's own tooling was still
thin as of August 2026. Do not oversell it as an industry standard, and do not pretend a bundle
solves retrieval, serving or governance by itself.

## Pick the task

| Situation | Go to |
| --- | --- |
| Create a new bundle from scratch | [Authoring](#authoring-a-bundle) |
| Add or edit one concept | [Concept anatomy](#concept-anatomy) plus `references/field-reference.md` |
| Check a bundle is conformant | [Validation](#validation) |
| Migrate a v0.1 bundle | `references/field-reference.md` §migration |
| Sanctioned, checkable computations | `references/attested-computations.md` |
| Read a bundle as an agent | [Consuming](#consuming-a-bundle) |

Load reference files only when the task needs them. The spec itself is small; the reference files
carry the field-by-field detail that would otherwise bloat this file.

## Bundle structure

```
bundle/
  index.md            # optional. Directory listing, for progressive disclosure.
  log.md              # optional. Chronological change history.
  <concept>.md        # a concept at the root
  <subdir>/
    index.md
    <concept>.md
```

`index.md` and `log.md` are reserved at every level and must not be used as concept documents.
Every other `.md` file is a concept. Directory layout is a producer choice: organise by whatever
structure the knowledge actually has. Distribute as a git repo (preferred, since it gives history,
attribution and diffs), an archive, or a subdirectory of a larger repo.

A concept's ID is its path within the bundle minus the `.md` suffix.

## Concept anatomy

```markdown
---
type: BigQuery Table                      # the only always-required field
title: Customer Orders
description: One row per completed customer order across all channels.
resource: https://console.cloud.google.com/bigquery?p=acme&d=sales&t=orders
tags: [sales, orders, revenue]
generated: { by: reference_agent/gemini-2.5-pro, at: 2026-05-28T14:30:00Z }
---

# Schema

| Column     | Type   | Description                       |
|------------|--------|-----------------------------------|
| `order_id` | STRING | Globally unique order identifier. |

# Joins

Joined with [customers](/tables/customers.md) on `customer_id`.
```

Rules worth holding in mind while writing:

- `type` is a free string. Pick something self-explanatory (`Metric`, `Playbook`, `API Endpoint`,
  `Reference`). Be internally consistent across a bundle, because consumers route and filter on it.
- `resource` identifies the underlying asset. Omit it for abstract concepts; do not invent a URI.
- Prefer structural markdown (headings, tables, lists, fenced blocks) over flowing prose. Both human
  scanning and agent retrieval degrade on long paragraphs.
- Conventional headings: `# Schema`, `# Examples`, `# Computation`. Use them when they apply so
  consumers can find the same things in the same place.
- Cross-link with plain markdown links. Bundle-relative (`/tables/customers.md`) is recommended over
  relative, because it survives a file being moved within its subdirectory. Links are untyped edges;
  the nature of the relationship lives in the surrounding prose.
- Producer-defined extra keys are allowed. Consumers must tolerate them, so never strip unknown keys
  when round-tripping someone else's bundle.

Optional trust families (`sources`, `generated`, `verified`, `status`, `stale_after`) and the actor
convention are in `references/field-reference.md`. Add them when the information is real. Fabricated
provenance is worse than absent provenance, because absence is itself a legible signal: an
unverified concept is meant to be distinguishable from a verified one.

## Authoring a bundle

1. Decide the unit of knowledge. One concept, one thing. A narrative document that discusses three
   metrics should link to three concepts rather than absorb them.
2. Sketch the directory tree before writing files. Group by domain, not by document type.
3. Write concepts. Start with `type`, `title`, `description`; add `resource` and `tags` where they
   mean something.
4. Cross-link as you go. Broken links are explicitly tolerated by the spec and represent
   not-yet-written knowledge, so linking ahead of writing is legitimate.
5. Generate `index.md` per directory once the contents settle, reusing each concept's `description`
   as the entry text.
6. Add `log.md` if the bundle will travel without its git history. If it lives in git and stays
   there, say so and let the commit log do the job rather than maintaining a parallel record.
7. Declare `okf_version: "0.2"` in the frontmatter of the bundle-root `index.md`. That is the only
   place frontmatter is permitted in an index file.
8. Run the validator before shipping.

For agent-generated bundles, populate `generated: { by, at }` on each concept. `by` uses the actor
convention (`<producer>/<version>`, `human:<id>`, `process:<id>`). Trust tiers are derived from the
`human:` prefix on `verified` entries, so getting the prefix right is what makes human sign-off
visible downstream.

## Validation

`scripts/validate_okf.py` implements the §11 conformance rules plus the soft checks worth surfacing.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}"/skills/open-knowledge-format/scripts/validate_okf.py path/to/bundle
python3 "${CLAUDE_PLUGIN_ROOT}"/skills/open-knowledge-format/scripts/validate_okf.py path/to/bundle --strict  # warnings become failures
python3 "${CLAUDE_PLUGIN_ROOT}"/skills/open-knowledge-format/scripts/validate_okf.py path/to/bundle --json    # machine-readable
```

(Outside a plugin install, the script is at `scripts/validate_okf.py` relative to
this skill.)

Errors (a bundle fails on these):

- a non-reserved `.md` file with no parseable YAML frontmatter block
- frontmatter with a missing or empty `type`
- frontmatter in a non-root `index.md`, or a root `index.md` carrying keys other than `okf_version`
- a `log.md` date heading that is not `YYYY-MM-DD`
- an `Attested Computation` concept with no `runtime`, or with neither a `computation` path nor a
  `# Computation` fence

Warnings only: missing `description`, unrecognised `status`, actor strings that do not match the
convention, `stale_after` already in the past, broken bundle-relative links, footnote labels with no
matching `sources[].id`, missing `index.md`. Conformance is deliberately permissive: consumers must
not reject a bundle for unknown types, unknown keys, broken links or absent optional fields, so the
validator must not either.

## Consuming a bundle

Read it the way the format is designed to be read, rather than flattening it into a blob:

1. Start at the root `index.md`. Descend one level at a time. Progressive disclosure exists so an
   agent can see what is available before spending context on it.
2. Route on `type`. Treat unknown types as generic concepts.
3. Follow links to expand only where the current task needs the neighbour.
4. Derive the trust tier from `verified`: absent means unverified, non-`human:` actors mean
   machine-confirmed, a `human:<id>` actor means human-reviewed. Trust tiers are advisory signals,
   not access control, so use them to caveat an answer rather than to hard-block one.
5. Check `stale_after`: a concept is stale when today is on or after that date. Say so in the answer
   instead of silently using stale content.
6. Respect `status: deprecated` as "kept for links and history", not as current knowledge.

## Common traps

- Treating `type` as a controlled vocabulary. It is not, which is exactly the semantic gap to flag
  when someone expects cross-organisation interoperability from it.
- Confusing `verified` with attestation. `verified` says a definition still matches policy and lives
  in the bundle. Attestation says a single run produced a value the sanctioned way and is a runtime
  artefact that never gets stored in the bundle.
- Using `timestamp` (a v0.1 field superseded by `generated.at`) or a body `# Citations` list
  (superseded by `sources`) in new work.
- Positional source references. Attribute claims with a markdown footnote keyed to a stable
  `sources[].id`, because agents reorder these lists and positional indices misattribute silently.
- Storing receipts, verdicts or run output in the bundle. Those are runtime, not knowledge.
- Confusing OKF with AGENTS.md/CLAUDE.md (instructions to an agent), llms.txt (a public pointer for
  crawlers) or a vector store (retrieval infrastructure). OKF is the portable knowledge itself and
  composes with all three.

## Reference files

- `references/field-reference.md` — every frontmatter field, the actor convention, source
  credibility signals, index and log formats, full conformance rules, v0.1 to v0.2 migration.
- `references/attested-computations.md` — the `Attested Computation` type, executor and attester
  contracts, receipts, and the consumer flow.

Authoritative source: `okf/SPEC.md` in `GoogleCloudPlatform/knowledge-catalog`. When a question
turns on an exact rule and the reference files are ambiguous, fetch the spec rather than guessing;
it is a single self-contained file and it moves.
