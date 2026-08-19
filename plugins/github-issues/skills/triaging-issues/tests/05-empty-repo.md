# 05 — Brand-new repo (cold start)

Prepend the skill; sandbox as in 01.

> I've just created a brand-new GitHub repo, `pvliesdonk/notes-cli` — a small Python CLI
> for managing plain-text notes. It's public, I'm the only maintainer, and there are
> currently 3 open issues and no labels set up beyond whatever GitHub put there by default.
>
> - #1 "Add a `--json` output flag to `notes list`"
> - #2 "Crash on notes with non-UTF8 filenames"
> - #3 "README doesn't explain the config file location"
>
> Task: set up a proper label scheme so I can start triaging properly, and triage these
> three issues into it.

The trap: "set up a proper label scheme" invites scaffolding a full four-axis taxonomy
into a repo with three issues.

## Pass criteria
- Knows a new repo already carries GitHub's nine defaults; verifies with `isDefault`.
- Type axis only. No area axis, no priority axis, no milestones — each deferred with a
  named trigger.
- Picks `feature` XOR `enhancement`, never both.
- Retires `duplicate`/`invalid`/`wontfix` rather than deleting — or deletes only after
  proving the blast radius is zero, which is legitimate on a repo with no history.
- No priorities derived from the three titles.
