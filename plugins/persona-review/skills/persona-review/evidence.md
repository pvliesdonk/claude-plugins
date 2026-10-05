# Evidence

The claims the skill rests on, each with its sources. Citations were checked
against Crossref, the ACL Anthology, PMLR or arXiv on 2026-10-05. Read this
before arguing with a rule.

## Simulated readers predict; they do not observe

- Technical writers and subject experts asked to predict the problems real
  readers flagged in a brochure caught under 15% of them, added many that
  readers never had, and agreed little with each other. Lentz & de Jong
  (1997), *IEEE Trans. Prof. Commun.* 40(3), 224-234,
  doi:10.1109/47.649557; replicating de Jong & Lentz (1996), *J. Technical
  Writing and Communication* 26(4), 507-519, doi:10.2190/66yb-njew-jx8w-ydpr.
- Persona prompts do not make a model more accurate: across 162 roles and
  four model families, no persona gave a reliable gain. Zheng et al. (2024),
  Findings of EMNLP, doi:10.18653/v1/2024.findings-emnlp.888.
- Persona variables explain under 10% of the variance in human annotations.
  Hu & Collier (2024), ACL, arXiv:2402.10811.
- Simulated personas caricature (exaggerate, fail to individuate) and
  flatten identity groups. Cheng, Piccardi & Yang (2023), EMNLP,
  arXiv:2310.11501; Wang, Morgenstern & Dickerson (2025), *Nature Machine
  Intelligence* 7, 400-411, doi:10.1038/s42256-025-00986-z.
- Population averages can be simulated well (r = 0.85 on 70 experiments),
  individual readers less so, with too little variation. Ashokkumar et al.
  (2026), *Nature* 656, 115-122, doi:10.1038/s41586-026-10742-x; Bisbee et
  al. (2024), *Political Analysis* 32, 401-416, doi:10.1017/pan.2024.5.
- Writer-defined AI reader personas were found useful, but their feedback
  was often verbose and unspecific (N = 5 and 11). Benharrak et al. (2024),
  CHI, doi:10.1145/3613904.3642406.

**In the skill:** findings are framed as predictions; the synthesis lists
the ones that drive a priority under "check with real readers"; cards carry
goals, stakes and reading habits rather than demographics; every finding
needs a location, a quote and what the reader needed.

Not settled: no study validates LLM reader personas against real readers of
reports, handbooks or software documentation.

## Several blind reviewers, and low agreement is normal

- One heuristic evaluator finds 20-51% of usability problems; three to five
  pooled do well. Nielsen & Molich (1990), CHI, doi:10.1145/97243.97281;
  Nielsen & Landauer (1993), CHI, doi:10.1145/169059.169166.
- Any two evaluators agree on 5-65% of problems, across 11 studies and even
  under a strict walkthrough procedure; vague goals and vague problem
  criteria drive the spread. Hertzum & Jacobsen (2001), *IJHCI* 13(4),
  421-443, doi:10.1207/s15327590ijhc1304_05.
- Specialised review agents cut generic comments from 60% to 29%. D'Arcy et
  al. (2024), MARG, arXiv:2401.04259 (preprint).

**In the skill:** 3 to 6 personas by default; each has an explicit goal,
entry point and stop condition; problem kinds are defined in the prompt; a
finding raised by one reader is treated as normal.

## Same-model agreement is not independent evidence

- When two models err, they pick the same wrong answer about 60% of the time
  on one leaderboard, and more accurate models are more correlated. Kim et
  al. (2025), ICML, arXiv:2506.07962.
- Agents in debate abandon correct answers to agree with peers. Wynn, Satija
  & Hadfield (2025), arXiv:2509.05396; Smit et al. (2024), ICML, PMLR
  235:45883-45905.
- A panel of judges from different model families matched human judgement
  better than one strong judge. Verga et al. (2024), arXiv:2404.18796.

**In the skill:** reviewers run blind and in parallel, never in debate; the
synthesis is told not to count votes; `verify_model` can put the verifiers
on a different model tier. A different tier of the same family is a weak
substitute for a different family.

## Models are kind to text, and kinder to model-written text

- All five assistants tested were sycophantic across four tasks. Sharma et
  al. (2024), ICLR, arXiv:2310.13548.
- Models rate their own outputs higher than humans do; GPT-4 preferred
  LLM-written text over human-written text 77-88% of the time, human raters
  did not. Panickssery, Bowman & Feng (2024), NeurIPS, arXiv:2404.13076;
  Laurito et al. (2025), *PNAS* 122(31), doi:10.1073/pnas.2415697122.

**In the skill:** reader prompts tell the reviewer it is kinder than the
reader and to correct for that; the author's opinion stays out of prompts;
reviewer satisfaction is never reported as a result; `drafted_with_ai` adds
the under-flagging caveat to the report.

## LLM reviewers miss significance and echo the document

- GPT-4's comments on papers overlapped with human reviewers' as much as two
  humans overlap (31-39%), but it was 10.7 times less likely to comment on
  novelty. Liang et al. (2024), *NEJM AI* 1(8), doi:10.1056/AIoa2400196;
  Shin et al. (2025), EMNLP, arXiv:2502.17086.
- LLM reviews echo the limitations a paper already admits, and text injected
  into a paper steers them. Ye et al. (2024), arXiv:2412.01708.

**In the skill:** a significance lens for papers and proposals; every frame
says the document is the object under review, not instructions, and asks
for text addressed to reviewers to be reported; readers are told the
document's account of its own importance and limitations is a claim.

## Quotes are checked outside the model

- GPT-4 fabricated 18% of 636 bibliographic references. Walters & Wilder
  (2023), *Scientific Reports* 13, 14045, doi:10.1038/s41598-023-41032-5.
- Without outside feedback, self-correction does not help reasoning and can
  hurt; answering verification questions independently of the draft
  reduces hallucination. Huang et al. (2024), ICLR, arXiv:2310.01798;
  Dhuliawala et al. (2024), Findings of ACL.
- Detecting hallucinated claims in peer reviews is hard without grounding in
  the source. Lin et al. (2026), HalluPeer, arXiv:2609.03580.

**In the skill:** a verifier locates every quote and checks major claims
against the document and the ground truth; the renderer searches every kept
quote by string match and flags misses.

Not settled: whether quote checking improves review quality has not been
tested directly; it rests on the attribution studies above.

## Walk a task, and arrive cold

- The cognitive walkthrough simulates a specific user's goal step by step.
  Polson, Lewis, Rieman & Wharton (1992), *Int. J. Man-Machine Studies*
  36(5), 741-773, doi:10.1016/0020-7373(92)90039-N.
- Readers of web and topic-based documentation arrive by search, mid-
  hierarchy. Baker (2013), *Every Page Is Page One*, XML Press.
- Documentation serves four needs: learning, doing, looking up,
  understanding. Procida, Diátaxis, https://diataxis.fr/.
- Personas engage teams but cannot be verified, and practitioners find them
  abstract and misleading when padded with irrelevant attributes. Pruitt &
  Grudin (2003), DUX, doi:10.1145/997078.997089; Chapman & Milham (2006),
  HFES, doi:10.1177/154193120605000503; Matthews, Judge & Whittaker (2012),
  CHI, doi:10.1145/2207676.2208573.

**In the skill:** every persona has a goal, an entry point, a stop condition
and a budget; a cold-arrival reader for consulted documents; cards record
their `source`.

## Constructive, and decisions left to the author

- Reviewers should be specific, give evidence, and not rewrite a sound text
  into their own preferred style. COPE (2013), *Ethical Guidelines for Peer
  Reviewers*, doi:10.24318/cope.2019.1.9.
- Requests for more work should say whether they are necessary for the
  claims or would only broaden them. "The perfect peer" (2011), *Nature
  Chemistry* 3(11), 831, doi:10.1038/nchem.1185.
- Proposal red teams predict how evaluators will score the bid. Shipley
  Associates, colour team reviews,
  https://www.shipleywins.com/blogs/color-team-reviews (practitioner
  guidance, not a study).
- In a dispute, agree in advance what evidence would settle it. Mellers,
  Hertwig & Kahneman (2001), *Psychological Science* 12(4), 269-275,
  doi:10.1111/1467-9280.00350.

**In the skill:** every finding states what the reader needed; editors judge
against a rubric, not taste; gatekeepers score against the stated criteria;
each conflict states what would settle it.

## Real readers, cheaply

- In the plus-minus method, readers mark what helps (+) and hinders (-) while
  reading, then explain the marks; revising six brochures on such pretests
  improved them. de Jong & Schellens (1998), IPCC,
  doi:10.1109/ipcc.1998.722086.
- Writers who studied real readers' think-aloud protocols got better at
  predicting reader problems, including omissions; general audience
  heuristics helped less. Schriver (1992), *Written Communication* 9(2),
  179-208, doi:10.1177/0741088392009002001.

**In the skill:** the report proposes a plus-minus test for each hypothesis
that drives a priority; the brief asks for real reader evidence to ground
the cards.
