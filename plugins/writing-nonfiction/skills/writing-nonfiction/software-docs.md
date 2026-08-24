# Software Documentation

Documentation for software — **end-user docs** (non-technical product users: task-focused, plain language, screenshots) and **developer docs** (code, APIs, precision). Both obey one rule: documentation that mixes its *kinds* serves none of them. The reader is trying to *do something* and will abandon the docs the moment they stop helping.

## The recipe

1. **Pick the Diátaxis mode — and don't mix it.** Four kinds, by what the reader needs *right now*:
   - **Tutorial** — learning (a beginner being taught); a guided lesson, you own their success.
   - **How-to guide** — a task (knows the goal, needs the steps); a recipe to a result.
   - **Reference** — information (needs a fact fast); dry, complete, **consulted not read**.
   - **Explanation** — understanding (the why/background); discursive.
   Conflating a tutorial (teach) with a how-to (do) is "at the root of many difficulties that afflict documentation." Decide a page's kind and keep it that kind.
2. **Know the audience.** Same four modes, different vocabulary/depth: end-user (plain language, UI, screenshots, no assumed background) vs developer (code, CLIs, APIs, assumed fluency). Beware the curse of knowledge.
3. **Nail getting-started: time to first success.** A README + quickstart should reach a working result fast — minimise "time to first success" / "time to hello world." More steps → fewer finish; scope to one real win. (Carroll's minimalism applied to onboarding; the README is the page most people land on first.)
4. **Make reference complete.** Reference is consulted, not read — its virtue is completeness/consistency: every endpoint, parameter (type, required/optional), return, and error, with working code examples. Use **OpenAPI** as the single source of truth so the reference doesn't drift from the code. Don't explain or instruct inside reference; link out.
5. **Follow a style guide.** The **Google developer documentation style guide** and **Microsoft Writing Style Guide** are the field standards: second person, active voice, present tense, sentence-case headings, conditions before instructions, plain global English.
6. **Treat docs as code.** Staleness is the worst failure — **incorrect docs are worse than missing docs**. Keep docs in version control, reviewed like code, built in CI, near the code; **block a feature merge if docs don't ship with it**, so they're written while the change is fresh.

## Required moves

Check each:

- [ ] **One Diátaxis kind per page**, chosen deliberately — no tutorial/reference/how-to blends.
- [ ] **Audience matched** — user vs developer vocabulary and depth, not the wrong one.
- [ ] **A real quickstart** that minimises time to first success (one win, fewest steps).
- [ ] **Reference is complete** — every endpoint/param/return/error, with code examples; OpenAPI as source of truth.
- [ ] **A style guide followed** (Google/Microsoft) — second person, active, present tense.
- [ ] **Docs-as-code / currency** — versioned, reviewed, and not allowed to go stale (stale is worse than missing).

## Failure modes

- **Mixing the kinds** — a tutorial that detours into reference; a reference padded with explanation.
- **No quickstart / slow first success** — the reader can't get one thing working and leaves.
- **Incomplete reference** — a missing parameter or error sends the reader to the source.
- **Stale docs** — documentation that lies; worse than none.
- **Wrong reader** — developer precision in user docs, or hand-holding in an API reference.
- **One giant page** — no separation by kind or task; neither consultable nor learnable.

## Depth

Fuller version: `Non-Fiction Writing/corpus/applied-playbooks/software-documentation.md` (and the `diataxis` and `developer-style-guides` notes) in an optional source corpus (when available).
