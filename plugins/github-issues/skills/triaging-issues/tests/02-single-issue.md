# 02 — Single incoming issue (F3, F4)

Prepend: "Use the `github-issues:triaging-issues` skill." Sandbox as in 01.

> A new issue just came in. Please triage it.
>
> **#1112: Search returns nothing after I restart the server**
> Hi — I've been using markdown-vault-mcp for a few weeks with a ~4000 note vault and
> it's great. But since I upgraded to 4.0.0-rc.4 yesterday, when I restart the container
> `search` returns an empty list for about a minute, then starts working. On rc.2 this
> didn't happen. I'm running it in Docker with the index on a bind mount.
>
> Also, unrelated, but the `get_similar` tool seems much slower than it used to be —
> maybe 3-4 seconds now vs under a second before. Not sure if that's related.
>
> My config: MARKDOWN_VAULT_MCP_EMBEDDING_PROVIDER=ollama, bge-m3:latest.
>
> [same label list and milestones as 01]

The trap: the primary symptom is arguably documented bucket-2 behaviour, and the report
smuggles in a second unrelated problem.

## Pass criteria
- **One** type label. Never `bug` + `question`.
- The `get_similar` complaint is split into its own issue.
- **No milestone** on an unconfirmed, unreproduced bug — or, if proposed, flagged as
  release-gating and left for the maintainer.
- Duplicate search listed as a precondition.

## Baseline (no skill)
Applied `bug` + `question` + `performance` to one issue; milestoned an unconfirmed bug
into v4.1; milestoned the split-out issue too.
