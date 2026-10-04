# Evidence

Condensed claims behind `SKILL.md`, each with its source. The full reference,
with quotations, access dates and the claims marked unverified, is
`docs/design/reference/agent-instruction-files.md` in
[pvliesdonk/fastmcp-server-template](https://github.com/pvliesdonk/fastmcp-server-template/blob/main/docs/design/reference/agent-instruction-files.md).
Sources were read on 2026-10-04.

## How the file reaches the model

- Claude Code delivers `CLAUDE.md` as a user message after the system prompt;
  it is "context, not enforced configuration". A hook is deterministic; the
  file is advisory. Imports load at launch and do not reduce context cost;
  only `.claude/rules/*.md` with a `paths` field loads on demand.
  [Claude Code, How Claude remembers your project](https://code.claude.com/docs/en/memory)
- Only a skill's name and description are loaded at startup; the body loads
  when invoked. [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- Codex concatenates the `AGENTS.md` chain, nearest file last, and stops at
  32 KiB. [Codex, AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
- Cursor: four application modes; keep a rule under 500 lines; add rules only
  when the agent repeats a mistake. [Cursor, Rules](https://cursor.com/docs/context/rules)
- Copilot: instructions "no longer than 2 pages", "not task specific".
  [GitHub Docs, repository custom instructions](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions)
- `AGENTS.md` is plain Markdown; nearest file wins; the user's prompt
  overrides it. [agents.md](https://agents.md/)

## What belongs in the always-loaded file

- Include: commands the agent cannot guess, style rules that differ from
  defaults, test runners, repository etiquette, project-specific architecture
  decisions, environment quirks, gotchas. Exclude: anything inferable from
  code, standard conventions, API documentation, volatile facts, "long
  explanations or tutorials", file-by-file descriptions, self-evident
  practices. Per line: "Would removing this cause Claude to make mistakes? If
  not, cut it." [Claude Code, Best practices](https://code.claude.com/docs/en/best-practices)
- Repository overviews, present in 95 to 100 percent of generated context
  files, did not help agents find files faster. Explicit tool instructions
  were followed (uv used 1.6 times per instance when named, 0.01 when not). A
  context file should "only contain specific additional instructions beyond
  what is already available in the codebase". Gloaguen et al.,
  [arXiv 2602.11988](https://arxiv.org/abs/2602.11988).
- Guidance that raised SWE-bench Verified resolve rate from 25.5 to 33.0
  percent was 47 percent procedural guardrails, 30 percent pointers to
  specific files, 23 percent quality gates; generic lines were replaced by
  specific ones; the gain came from reaching the right file. Capped at 3,000
  characters by trimming boilerplate and the longest bullets. Shepard and
  Albrecht, [arXiv 2606.20512](https://arxiv.org/abs/2606.20512).
- "Concrete instructions beat aspirational ones"; `AGENTS.md` is guidance,
  not enforcement. [AAIF, Measuring AGENTS.md](https://aaif.io/blog/measuring-agents-md-what-five-runs-show-that-one-doesn-t)
- The system prompt holds "the minimal set of information that fully
  outlines your expected behavior", at an altitude between brittle hardcoded
  logic and vague guidance. [Anthropic, Effective context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

## Length, instruction count and adherence

- Target under 200 lines; longer files "reduce adherence"; a bloated file
  makes Claude "ignore your actual instructions"; a rule the agent keeps
  skipping means "the file is probably too long and the rule is getting
  lost". [Claude Code, memory](https://code.claude.com/docs/en/memory) and
  [best practices](https://code.claude.com/docs/en/best-practices)
- Adherence degrades with instruction density, with a bias toward earlier
  instructions; the best models reach 68 percent at 500 instructions.
  Jaroslawicz et al., IFScale, [arXiv 2507.11538](https://arxiv.org/abs/2507.11538).
- "An important factor contributing to this trend is the degree of tension
  and conflict that arises as the number of instructions is increased." Elder
  et al., [arXiv 2510.14842](https://arxiv.org/abs/2510.14842).
- Contradicting instructions make Claude "pick one arbitrarily";
  `/doctor prompt-audit` finds stale and conflicting instructions.
  [Claude Code, memory](https://code.claude.com/docs/en/memory)
- No dependency between context-file length and success or cost; the cost
  comes from following what the file says (more reads, more test runs, 22
  percent more reasoning tokens). Gloaguen et al.
- A present `AGENTS.md` cut median runtime 28.64 percent and output tokens
  16.58 percent at comparable completion. Lulla et al.,
  [arXiv 2601.20404](https://arxiv.org/abs/2601.20404).
- A twelve-line file cut wall time 27 percent on an ambiguous task over five
  runs; single runs misled. AAIF, above.
- Skill bodies: under 500 lines; "Claude is already very smart"; challenge
  each paragraph with "Does this paragraph justify its token cost?".
  [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)

## Wording

- "Concrete enough to verify": `Use 2-space indentation`, not `Format code
  properly`. [Claude Code, memory](https://code.claude.com/docs/en/memory)
- "Tell Claude what to do instead of what not to do." Motivation helps Claude
  generalise: the text-to-speech example. [Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- Emphasis: "add emphasis such as 'IMPORTANT' to that line alone. If you
  emphasize many lines, none of them stands out." [Claude Code, best practices](https://code.claude.com/docs/en/best-practices)
- Opus 4.5 and later over-trigger on "CRITICAL: You MUST"; write "Use this
  tool when...". [Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- Sonnet 5 "interprets prompts literally" and "does not silently generalize
  an instruction from one item to another"; "be conservative" in a review
  prompt lowers recall, so "be concrete about where the bar is".
  [Prompting Claude Sonnet 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5)
- Opus 5 writes longer documents than earlier models and adds verification
  steps on its own; verification and "double-check" instructions are to be
  removed; positive examples beat negative instructions.
  [Prompting Claude Opus 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5)
- Match freedom to fragility; a default with one escape hatch; one term per
  concept; evaluation-driven authoring; review a drafted skill for
  explanations Claude does not need. [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)

## Not measured by any source

- Whether a hedge ("prefer", "consider") is read as absolute or optional.
  The literal-following notes above are the nearest evidence.
- The adherence cost of rationale sentences as such.
- The split this skill draws between a rationale clause that decides an
  unlisted case and one that justifies the rule to a human.
