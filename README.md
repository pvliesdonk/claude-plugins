# pvliesdonk Claude Code Plugin Catalog

A [Claude Code](https://claude.ai/code) plugin marketplace catalog for pvliesdonk's projects.

## Installation

Add this catalog to Claude Code:

```
/plugin marketplace add pvliesdonk/claude-plugins
```

Then install any plugin:

```
/plugin install markdown-vault-mcp
```

## Available Plugins

### markdown-vault-mcp

A generic markdown collection MCP server with FTS5 + semantic search, frontmatter-aware indexing, and incremental reindexing.

- **Source:** [pvliesdonk/markdown-vault-mcp](https://github.com/pvliesdonk/markdown-vault-mcp)
- **Version:** 1.20.1

### preflight-circus

A blind six-lens review gate over `BASE..HEAD`, run before you push rather than
after — the same examination a post-push review bot applies, sat while the diff
is still local. Ships a skill and the Workflow script it drives.

- **Source:** [`plugins/preflight-circus`](plugins/preflight-circus) — in this repository
- **Details:** [plugin README](plugins/preflight-circus/README.md)

## License

MIT — see [LICENSE](LICENSE)
