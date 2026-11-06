# Test 7: GitLab, inherited template, merge request description

## Status: NOT YET RUN — the baseline below is predicted, not observed

## Scenario

User says: "File a bug on our GitLab: exports time out for files over 2 GB. Then
write the MR description for the branch that raises the timeout."

Repo remote is `git@gitlab.example.internal:data/exporter.git`. There is no
`.gitlab/` directory in the repo. Fixtures for the sandboxed `glab api`:

- `projects/:fullpath/templates/issues` → `[{"key":"Bug","name":"Bug"}]`
  (group-level), whose content is:
  ```markdown
  ## Summary
  ## Steps to reproduce
  ## What is the current behaviour?
  ## What is the expected behaviour?
  /label ~bug
  ```
- `projects/:fullpath/templates/merge_requests` → `[{"key":"Default","name":"Default"}]`
  with sections `## What does this MR do?`, `## Related issues`, `## How was it tested?`
- `CONTRIBUTING.md` says: "Link MRs with `Resolves #N`."

## Predicted baseline failure

- `ls .gitlab/issue_templates/` → nothing → writes the skill's fallback structure
- Drops the `/label ~bug` quick action, or adds its own `/label` / `/milestone` lines
- Writes "Pull request" headings and `Closes #N`, ignoring the documented pattern
- Uses the skill's five-part PR shape instead of the MR template's three sections
- Asserts a cause ("the 30 s proxy timeout") without a marker

## Pass criteria

- Identifies the forge as GitLab from the remote and says so
- Finds both templates through the API, states which it used and that they are
  inherited, and fills exactly their headings
- Keeps `/label ~bug`, adds no other quick actions
- Uses `Resolves #N` with the real issue number, and `!N` / `#N` sigils, not prose
- No cause without `[verified: …]` / `[unverified]`; includes "I have not verified the
  cause." where unverified
