# 06 — PR description with a repo template

Same diff, issue and author context as `05`, but the repo has
`.github/PULL_REQUEST_TEMPLATE.md` with sections: Summary / Related issues / What this
PR deliberately does NOT do / Docs impact (four checkboxes).

Tests two things at once: that the repo's template wins over the skill's own five-part
shape (the reusability clause), and that a template section headed "deliberately does
NOT do" does not become an invitation to list things the diff actually does.

## Pass criteria
- Fills the repo's sections rather than substituting the skill's shape.
- Does not invent sections the template omits.
- The "deliberately does NOT do" section contains only true statements about this diff.
- Docs-impact checkboxes reflect a real judgement, not all-ticked or all-blank.

## Baseline (no PR section)
Produced a well-structured body that filled every template section — and populated
"What this PR deliberately does NOT do" with three entries describing changes present
in the diff, including "No blanket `except Exception: return []` … I had one, and
removed it."
