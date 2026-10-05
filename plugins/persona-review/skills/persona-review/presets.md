# Starting ensembles

Cut every persona the document has no reader for, rename the rest to the
real readers, and run the distinctness test from SKILL.md step 2. Each
preset's *Source* line says how much running it has behind it.

## Practitioner handbook or field guide

*Source:* two rounds on a product-security handbook for small manufacturers.

| Key | Tier | Mode | Goal | Weighting |
|-----|------|------|------|-----------|
| `ceo` | primary | read | Decide whether this is a proportionate business case, and what exposure the signature carries | 70% experience |
| `cto` | primary | read | Turn advice into concrete engineering work; spot vague or stack-assuming advice | 50/50 |
| `owner` | primary | walk | Carry out one instructed step on Monday morning, arriving at its section from the contents or a link | 40% experience |
| `procurement` | secondary | walk | Build purchase-order questions and a supplier register from the book | 50/50 |
| `production` | secondary | read | Know what changes on the shop floor, and what it costs in training and takt time | 60% experience |
| `expert` | adversarial | read | Find what is wrong, dated or dangerously simplified; separate "simplified for the audience" from "wrong" | 25% experience |
| `reach-region` | secondary | read | Use it outside the jurisdiction it is framed for | 60% experience |
| `reach-scale` | secondary | read | Find what applies to a much larger organisation, and what is safely skippable | 50/50 |

Lenses: a plain-English reading-experience editor (sentence length,
front-loading, meta-signposting, headings), and a consistency editor (house
conventions, running-example canon, terminology drift, one figure quoted two
ways, recurring rhetorical tics).

- Put the fact register in `ground_truth`: in one round it refuted four
  correctness findings that rested on a reviewer's recall.
- Put the deliberate design decisions in `design_context`, so several readers
  tripping on one decision reach the author as a decision, not as noise.
- In a later round, list the rewritten sections in `previous.rewritten`: the
  second round's new problems were consistency and length regressions in
  rewritten chapters.

## Software documentation site

*Source:* two rounds on an MCP server's documentation, about 63,000 words.

Every persona walks, with `coverage: path`. Match each to the Diátaxis need
it has: learning, doing a task, looking something up, or understanding.

| Key | Tier | Entry | Goal and stop condition | Budget |
|-----|------|-------|-------------------------|--------|
| `evaluator` | gatekeeper | README or landing page | A go/no-go on replacing what they use now | 1,000 (5 min) |
| `newcomer` | primary | Installation | A working first call tonight; has never run this kind of server | 4,000 (20 min) |
| `self-hoster` | primary | Deployment index | An authenticated deployment for a small team | 9,000 (45 min) |
| `power-user` | secondary | Search, or the guides index | One advanced feature configured; reads long guides | 6,000 (30 min) |
| `library` | secondary | API reference | The library used from their own code, not the server | 3,000 (15 min) |
| `llm-client` | primary | `llms.txt` and the tool descriptions (`reader_files` override) | Correct tool plans for five tasks; no human reads what it reads | 22,000 (30k tokens) |
| `upgrader` | secondary | Release notes | Whether the new release breaks their deployment | 2,000 (10 min) |
| `contributor` | secondary | CONTRIBUTING | Where a change goes, and what must change with it | 12,000 (60 min) |

- Put the source code in `ground_truth`: checking teach-backs against it
  surfaced Python examples that fail as written and a "read-only" setup that
  ran read-write.
- Expect two of these to collapse into one for a smaller project; the
  newcomer and self-hoster were the suspected pair.
- Compare rounds by blockers per walk, teach-back verdicts and words read
  against budget.

## Scientific paper

*Source:* the author's runs on a paper; briefs not preserved, so this
ensemble is reconstructed.

| Key | Tier | Mode | Goal |
|-----|------|------|------|
| `field-expert` | primary | read | Judge whether the contribution is real and correctly placed in the literature |
| `adjacent-a`, `adjacent-b` | secondary | read | Scientists from two neighbouring fields: can they follow the argument and use the result? |
| `pc-reviewer` | gatekeeper | walk | Score each of the venue's criteria (in `came_for`): novelty, significance, soundness, clarity; stop at a recommendation |
| `adversary` | adversarial | read | Restate the claim fairly, then find the weakest link and say what evidence would answer each objection |

Lenses: a significance lens (what is new, why it matters, compared with
what), and the venue's style guide or the author's house style.

## Thesis chapter

*Source:* derived from the paper ensemble; not yet run.

| Key | Tier | Mode | Goal |
|-----|------|------|------|
| `supervisor` | gatekeeper | read, `teach_back: true` | Decide whether the chapter is ready for the committee, and what it argues |
| `examiner` | adversarial | read | Find the claim least supported by the chapter's own evidence |

Add a field expert only when the author names one who will read it. Lenses:
the department's or university's thesis guidelines as rubric, and a
significance lens.

## Proposal or grant

*Source:* proposal colour-team practice, where a red team predicts how
evaluators will score the bid; not yet run.

| Key | Tier | Mode | Goal |
|-----|------|------|------|
| `evaluator` | gatekeeper | walk | Score each award criterion from the call (in `came_for`), with strengths, weaknesses and risks; stop at a score |
| `programme-officer` | gatekeeper | read | Check fit with the programme's aims and eligibility |
| `client-decider` | primary | read | For contract research: decide whether to buy, from the first page |
| `client-technical` | primary | read | Judge whether the work plan is credible and the team can do it |
| `competitor` | adversarial | read | Find where a rival bid would beat this one |

Lenses: a compliance lens with the call text as rubric (every required
section, page limit and criterion addressed), and a significance lens.

## Anything else

Start from the document's job: what a reader should do after reading it.
List who it is for, who decides whether it is accepted, who else reads it,
who reads it hostile, and who lands in the middle of it, and keep the ones
that exist. The writing-nonfiction skill's genre files, when installed, name
the readers each genre serves.
