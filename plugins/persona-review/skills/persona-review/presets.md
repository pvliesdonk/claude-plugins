# Starting ensembles

Starting points, not menus. Cut every persona the document does not have a
reader for, rename the rest to the real readers, and run the distinctness
test from SKILL.md step 2. Where a preset came from, and how often it has
run, is stated under each heading, so you know how much weight it carries.

## Practitioner handbook or field guide

From two rounds on a product-security handbook for small manufacturers.
Readers read the whole book (`coverage: whole`); weighting varies by role.

| Key | Tier | Goal | Weighting |
|-----|------|------|-----------|
| `ceo` | primary | Decide whether this is a proportionate business case, and what exposure the signature carries | 70% experience |
| `cto` | primary | Turn advice into concrete engineering work; spot vague or stack-assuming advice | 50/50 |
| `owner` | primary | Carry out each step on Monday morning, arriving at sections from the contents or a link | 40% experience |
| `procurement` | secondary | Build purchase-order questions and a supplier register from the book | 50/50 |
| `production` | secondary | Know what changes on the shop floor, and what it costs in training and takt time | 60% experience |
| `expert` | adversarial | Find what is wrong, dated or dangerously simplified; separate "simplified for the audience" from "wrong" | 25% experience |
| `reach-region` | secondary | Use it outside the jurisdiction it is framed for, without the framing getting in the way | 60% experience |
| `reach-scale` | secondary | Find what applies to a much larger organisation, and what is safely skippable | 50/50 |

Lenses: a plain-English reading-experience editor (GOV.UK/GDS rubric:
sentence length, front-loading, meta-signposting, headings), and a
consistency editor (house conventions, running-example canon, terminology
drift, the same figure quoted two ways, recurring rhetorical tics).

What the rounds showed: in one round, verifiers refuted four correctness
findings where a reviewer's recall lost to the fact register, so give
verifiers `ground_truth`; several naive readers independently hitting one
design decision was recorded as evidence about the design, not noise; the
second round found consistency and length regressions introduced by the
first round's rewrites, so a later round should name the rewritten sections.

## Software documentation site

From two rounds on an MCP server's documentation (about 63,000 words).
Readers walk a path (`coverage: path`) from a stated entry point, with a
budget, and end with a teach-back that verifiers check against the source
code. Match each reader to the Diátaxis need it has: learning, doing a task,
looking something up, or understanding.

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

What the rounds showed: checking walks against the code surfaced defects
the prose hid (Python examples that fail as written, a "read-only" setup
that ran read-write), so `ground_truth: ["src/"]` earns its cost; the issue
that started it already suspected two personas would collapse into one, so
run the distinctness test; blockers per walk, teach-back verdicts and words
read against budget made the two rounds comparable.

## Scientific paper

From the author's runs on a paper, briefs not preserved; the ensemble is
reconstructed. Readers read the whole paper.

| Key | Tier | Goal |
|-----|------|------|
| `field-expert` | primary | Judge whether the contribution is real and correctly placed in the field's literature |
| `adjacent-a`, `adjacent-b` | secondary | Scientists from two neighbouring fields: can they follow the argument and use the result? |
| `pc-reviewer` | gatekeeper | Score against the venue's criteria (list them in `came_for`): novelty, significance, soundness, clarity |
| `adversary` | adversarial | Restate the paper's claim fairly, then find the weakest link and say what evidence would answer each objection |

Lenses: a significance lens (what is new, why it matters, compared with what;
LLM reviewers otherwise rarely comment on novelty), and the venue's style
guide or the author's house style.

## Proposal or grant

Not yet run; derived from proposal colour-team practice, where the red team
predicts how evaluators will score the proposal. Use the call text or the
request for proposals as the rubric.

| Key | Tier | Goal |
|-----|------|------|
| `evaluator` | gatekeeper | Score each award criterion from the call (in `came_for`), with strengths, weaknesses and risks |
| `programme-officer` | gatekeeper | Check fit with the programme's aims and eligibility |
| `client-decider` | primary | For contract research: decide whether to buy, from the first page |
| `client-technical` | primary | Judge whether the work plan is credible and the team can do it |
| `competitor` | adversarial | Find where a rival bid would beat this one |

Lenses: a compliance lens with the call text as rubric (every required
section, page limit, criterion addressed), and a significance lens.

## Anything else

Start from the document's job (what a reader should do after reading it) and
list: who it is for, who decides whether it is accepted, who else will read
it, who reads it hostile, and who lands in the middle of it. Keep the ones
that exist. For the genre's structure and the moves writers skip, the
writing-nonfiction skill's genre files, when installed, name the readers each
genre serves.
