# OKF v0.2 field reference

Contents: [Frontmatter](#frontmatter) · [Provenance](#provenance-sources) ·
[Trust](#trust-generated-and-verified) · [Lifecycle](#lifecycle-status-and-stale_after) ·
[Actors](#actor-convention) · [Links and paths](#links-and-paths) · [index.md](#indexmd) ·
[log.md](#logmd) · [Conformance](#conformance) · [Migration](#migration-v01-to-v02)

## Frontmatter

A YAML block delimited by `---` at the very start of the file, closing `---` on its own line.
Everything after it is the body.

| Field | Status | Notes |
| --- | --- | --- |
| `type` | required | Free string. Not centrally registered. Consumers route, filter and present on it, and must tolerate unknown values. |
| `title` | recommended | Display name. Consumers may derive one from the filename if absent. |
| `description` | recommended | One sentence. Used by index generators, search snippets, previews. |
| `resource` | recommended | Canonical URI of the underlying asset. Absent for abstract concepts. |
| `tags` | optional | List of short strings. There is no tag-file format; a consumer wanting a tag view synthesises it by scanning frontmatter. |
| `sources` | optional | Provenance, below. |
| `usage_window` | optional | Sibling of `sources`; `{ from, to }` framing every `usage_count`. |
| `generated` | optional | `{ by, at }`, below. |
| `verified` | optional | List of `{ by, at }`, below. |
| `status` | optional | `draft` / `stable` / `deprecated`. Absent means `stable`. |
| `stale_after` | optional | Absolute date `YYYY-MM-DD`. |
| `runtime`, `parameters`, `computation`, `executor`, `attester` | conditional | Attested Computation only. See `attested-computations.md`. |
| `okf_version` | special | Only in a bundle-root `index.md`. |

Producers may add any other keys. Consumers should preserve unknown keys when round-tripping and
must not reject documents that carry them.

### Body

Free-form markdown, no required sections. Conventional headings: `# Schema` (an asset's
columns/fields), `# Examples` (usage, usually fenced), `# Computation` (an Attested Computation's
sanctioned computation). Structural markdown beats prose for both human and agent readers.

## Provenance: `sources`

```yaml
sources:
  - id: ga4-schema
    resource: https://developers.google.com/analytics/bigquery/export-schema
    title: GA4 BigQuery Export schema
    author: team:ga4-docs
    usage_count: 5000
    last_modified: 2026-05-30
usage_window: { from: 2026-06-01, to: 2026-06-30 }
```

- `resource` — required within an entry. Either something followable (absolute URL, bundle-relative
  path, path into `references/`) or a scope descriptor that cannot be followed, for example
  `all queries in BigQuery project X`.
- `id` — optional but present whenever the body cites the source, since it is the footnote join key.
- `title` — optional human label.

Credibility signals, all optional, all per-entry:

- `author` — who or what produced the source, in the actor convention. Authority signal.
- `usage_count` — how often the resource was exercised over `usage_window`. Adoption and liveness
  signal. Coarse: comparable at alive-versus-dead and order-of-magnitude level and against its own
  history, not as a cross-kind ranking. A scheduled query's executions and a human's deliberate
  dashboard views are not equivalent.
- `last_modified` — `YYYY-MM-DD`, when the source itself last changed. Distinct from `generated.at`,
  which is when the concept was written.

OKF stores signals, never a credibility score: a score is subjective, unportable and goes stale.
Credibility is inferred at consumption time, the same way trust tiers are.

Lineage rides on links rather than a dedicated field. When a `sources[].resource` points at another
concept in the bundle, the derivation edge already exists in the graph, so a consumer may recurse
into that concept's own `sources`. External leaf sources carry only their intrinsic signals. Explicit
`derived_from` and data lineage are out of scope in v0.2.

### Per-claim attribution

```markdown
The `events_` table is sharded daily as `events_YYYYMMDD`.[^ga4-schema]

[^ga4-schema]: GA4 BigQuery Export schema
```

The footnote label is the join key into `sources[].id`. Consumers resolve attribution through the
matching entry, not by parsing the footnote prose. Labels are keyed rather than positional because
agents rewrite these documents constantly and a positional index misattributes silently the moment
the list is reordered.

## Trust: `generated` and `verified`

```yaml
generated: { by: reference_agent/gemini-2.5-pro, at: 2026-06-20T22:53:05Z }
verified:
  - { by: human:ahormati, at: 2026-06-25T09:00:00Z }
  - { by: process:finance-nightly, at: 2026-06-26T02:00:00Z }
```

- `generated.by` — required within `generated`. An actor.
- `generated.at` — ISO 8601 datetime of the content's last meaningful change.
- `verified` — list of verification events, each `{ by, at }`. Multiple entries capture independent
  checks. "How recently" is the latest `at`.
- The two are independent: content can change without re-confirmation, and facts can be re-confirmed
  without regeneration. Who wrote a concept need not be who confirmed it.
- A single verifier may be written as a bare mapping without the list dash. Consumers must treat a
  bare mapping as a one-element list.

### Trust tiers

Derived, never stored:

| `verified` state | Tier |
| --- | --- |
| key absent | unverified |
| only non-`human:` actors | machine-confirmed |
| any `human:<id>` actor | human-reviewed |

Advisory signals, not access control. A concept with no trust frontmatter at all is still consumable
and must not be rejected.

## Lifecycle: `status` and `stale_after`

- `status: draft` — not yet reviewed, possibly incomplete.
- `status: stable` — default, ready for consumption.
- `status: deprecated` — kept for links and history, no longer current.
- `stale_after: 2026-09-23` — absolute date. Stale when `today >= stale_after`. Absolute rather than
  a relative TTL so staleness is a plain date comparison with no reference to read time.

## Actor convention

Used by `generated.by`, `verified[].by`, and `sources[].author`:

- `<producer>/<version>` for agents and tools, e.g. `reference_agent/gemini-2.5-pro`
- `human:<id>` for a person, e.g. `human:ahormati`
- `process:<id>` for an automated process, e.g. `process:finance-nightly`

Trust classification keys off the `human:` prefix, so hand-authored or human-confirmed content must
use it or the sign-off is invisible downstream.

## Links and paths

Two link forms:

- Bundle-relative, beginning with `/`, interpreted from the bundle root. Recommended: stable when a
  document moves within its subdirectory.
- Ordinary relative paths (`./other.md`, `../computations/revenue.md`).

Links are directed but untyped. A link asserts a relationship; which relationship (parent, joins-with,
depends-on) is conveyed by the surrounding prose. Consumers building a graph view treat all links as
edges of one untyped relation.

Broken links are not malformed. They may represent knowledge not yet written, and consumers must
tolerate them.

Path-valued fields (`resource`, `sources[].resource`, `computation`, `executor.resource`,
`attester.resource`) each accept an absolute URL, a bundle-relative path beginning with `/`, or a
relative path. A `sources[].resource` may alternatively be a scope descriptor, in which case it is
not a path at all.

A `references/` subdirectory conventionally mirrors external material, run instructions or code as
first-class concepts in the bundle. Sources, executors and attesters commonly point into it. It is a
naming convention, not a requirement.

## index.md

Optional in any directory including the root. Enumerates the directory's contents so a reader can
see what exists before opening anything.

No frontmatter, with exactly one exception: a bundle-root `index.md` may carry `okf_version`.

```markdown
# Section heading

* [Title 1](relative-url-1) - short description of item 1
* [Title 2](relative-url-2) - short description of item 2

# Another section

* [Subdirectory](subdir/) - short description of the subdirectory
```

Entries should reuse the linked concept's `description`. Producers may generate index files;
consumers may synthesise one when none is present.

## log.md

Optional at any level. Flat list of date-grouped entries, newest first. Date headings must be
ISO 8601 `YYYY-MM-DD`.

```markdown
# Directory Update Log

## 2026-05-22
* **Update**: Added a BigQuery table reference for [Customer Metrics](/tables/customer-metrics.md).
* **Creation**: Established the [Dataplex Playbook](/playbooks/dataplex.md).

## 2026-05-15
* **Initialization**: Created foundational directory structure.
```

Entries are prose. The leading bold word (`**Update**`, `**Creation**`, `**Deprecation**`) is a
convention, not a requirement. In a git-hosted bundle `log.md` largely duplicates the commit log; it
earns its keep when bundles travel without version-control history.

## Conformance

A bundle is conformant with v0.2 if:

1. every non-reserved `.md` file in the tree has a parseable YAML frontmatter block,
2. every frontmatter block has a non-empty `type`,
3. every present reserved file follows the `index.md` / `log.md` structure above.

Where the optional families appear, consumers:

- must treat a bare `verified` mapping as a one-element list,
- must not reject a concept for missing any optional family,
- should derive trust tiers and staleness only from the specified fields, and should surface rather
  than silently drop a failing attestation.

Everything else is soft guidance. Consumers must not reject a bundle for missing optional fields,
unknown `type` values, unknown extra keys, broken cross-links, or missing `index.md`.

## Versioning

`<major>.<minor>`. Minor bumps are backward-compatible additions; major bumps may rename required
fields or change reserved filenames. A bundle may declare `okf_version: "0.2"` in root `index.md`
frontmatter. A consumer that does not understand the declared version should attempt best-effort
consumption rather than refusing the bundle.

Deferred to future revisions: the full runtime protocol (receipt and verdict wire formats,
attestation lifecycle), the attester ABI and sandboxing, attestation caching, and semantic-layer
templates where the attester comparison shifts from SQL equality to model-and-binding equality.

## Migration v0.1 to v0.2

Two breaking changes:

- `timestamp` is superseded by `generated: { by, at }`. Consumers may fall back to a legacy
  `timestamp` when `generated` is absent.
- A body `# Citations` list is superseded by frontmatter `sources`. Consumers should read `sources`
  and may still parse a legacy `# Citations` list on v0.1 documents.

Everything else is additive, so a v0.1 bundle stays consumable:

- new families `sources` (plus `author`, `usage_count`, `last_modified`, `usage_window`),
  `generated`, `verified`, `status`, `stale_after`
- new type `Attested Computation` and its keys `runtime`, `parameters`, `computation`, `executor`,
  `attester`
- new conventional heading `# Computation`
- the actor convention for `generated.by` and `verified[].by`

Bundle structure, reserved filenames, the required `type`, the recommended
`title`/`description`/`resource`/`tags`, cross-linking, index files, log files and the permissive
conformance model all carry forward unchanged.

Practical migration order: rewrite `timestamp` into `generated`, lift `# Citations` into `sources`
with stable ids, convert in-body citation references into keyed footnotes, then add `status`,
`verified` and `stale_after` only where the underlying facts are real. Splitting multi-figure
documents into linked `Attested Computation` concepts is optional and only worth doing where a value
actually needs to be checkable.
