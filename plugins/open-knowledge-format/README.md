# open-knowledge-format

Working with **Open Knowledge Format (OKF)** bundles — authoring them, checking
conformance, migrating v0.1 to v0.2, and consuming them the way the format is meant
to be read.

OKF represents knowledge as a directory of markdown files with YAML frontmatter. No
SDK, no schema registry, no runtime: a conformant bundle is readable with `cat` and
shippable with `git clone`.

## Install

```
/plugin marketplace add pvliesdonk/claude-plugins
/plugin install open-knowledge-format
```

## What's in it

- **The skill** — bundle structure, concept anatomy, the authoring sequence, the
  consuming sequence, and the traps that actually catch people.
- **`references/field-reference.md`** — every frontmatter field, the actor convention,
  source credibility signals, index and log formats, the conformance rules, and the
  v0.1 → v0.2 migration.
- **`references/attested-computations.md`** — the `Attested Computation` type, the
  executor and attester contracts, receipts, and the consumer flow.
- **`scripts/validate_okf.py`** — a conformance validator implementing the §11 rules
  plus the soft checks worth surfacing. Stdlib only, PyYAML the single dependency;
  it reads and reports, and writes nothing.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}"/skills/open-knowledge-format/scripts/validate_okf.py path/to/bundle
```

Exit 0 clean, 1 on errors (or on warnings under `--strict`), 2 on bad invocation.
`--json` for machine-readable output.

## What it will tell you that a summary of the spec would not

The skill is deliberately honest about the format's limits, because overselling it
is the failure mode:

> OKF fixes structural interoperability … It does not fix semantic interoperability.
> There is no registry of `type` values, so two producers can describe the same thing
> incompatibly and both remain conformant.

It also keeps two things apart that are easy to conflate: `verified` says a
*definition* still matches policy and lives in the bundle; **attestation** says a
single *run* produced a value the sanctioned way, and is a runtime artefact that is
never stored in the bundle. And it holds a line on provenance — fabricated provenance
is worse than absent provenance, because absence is itself a legible signal.

## About the format

OKF is published by Google Cloud's Data Cloud team in the
[`GoogleCloudPlatform/knowledge-catalog`](https://github.com/GoogleCloudPlatform/knowledge-catalog)
repository (`okf/SPEC.md`, Apache 2.0). It is an early-stage spec rather than a
ratified standard, and its authors describe it as a starting point. This plugin is an
independent skill *about* that spec; it is not affiliated with or endorsed by Google.

Not to be confused with the Open Knowledge Foundation (okfn.org), an unrelated
non-profit sharing the abbreviation.

## Related

If you serve an OKF bundle as a vault,
[`markdown-vault-mcp`](https://github.com/pvliesdonk/markdown-vault-mcp) implements
the read-side annotations (type, status, staleness, trust tier) and ships
`okf_validate`, `okf_verify`, `okf_convert_links`, `okf_generate_index` and
`okf_seed_log` as MCP tools.
