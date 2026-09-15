# Processes, Mechanisms and Causal Claims

Process and causal material differs from magnitudes in one respect that governs everything else: the
cheapest mark on the picture — the arrow — is the most expensive claim on it. One drag of the mouse
asserts causation, or sequence, or a message, or a transfer, or mere adjacency, and the reader has to
guess which from a mark that looks identical in every case. The guess is not random; it is biased
towards causation, and that has been measured.

**Scope.** This file covers the judgment: which picture, at what level, making which claim. Diagram
syntax and layout — notation grammar, shapes, routing, rendering — belong to the `creating-diagrams`
skill. A file about what the picture should contain that starts recommending shapes has drifted.

## The recipe

1. **Say which of three pictures this is.** "A diagram of the system" is three non-substitutable
   artefacts. **Topology** answers "how is it wired, where would we change it?"; **behaviour over
   time** answers "how much, how fast, will it settle or oscillate?"; **one traced scenario** answers
   "how does this actually work?" Drawing the wrong one is the expensive mistake here and the hardest
   to catch, because all three arrive looking like a competent diagram. If the question contains "how
   long", "how much" or "will it overshoot", no topology picture will do. Put the answer at the top:
   "structure, not sequence" costs six words.
2. **Declare one abstraction level and hold it.** Finish the sentence: **"Every box on this picture
   is a ____."** One type — a team, a service, a step, a control, a supplier — and you have one
   diagram; an honest answer needing an "and" means you have two. Say which parent box a lower
   picture opens, and let level decide inclusion, not importance. The reader-side version is
   stronger: can someone who was not in your head name the type of every element? (Practitioner
   consensus, from C4 and its ladder — coherent and durable, but **no controlled evidence** compares
   level-consistent against level-mixed diagrams. Teach it as convention.)
3. **Name the pathology, then pick the form.** Process notations are filters: each makes one class of
   fact salient and structurally suppresses the rest. Waiting dominates → **value-stream map**; a
   flowchart *cannot* show it, because waiting is not a box — it lives in whitespace, and whitespace
   carries no label. Work gets dropped → **swimlane**, lanes as decision owners, not departments. A
   visible failure with an invisible upstream cause → **service blueprint**, whose line of visibility
   is what a journey map structurally lacks; most service failures originate below that line.
   Branching, exceptions, a compliance rule → **flowchart**. The room does not believe the experience
   is bad → **journey map**. If you cannot name a pathology you are documenting, not arguing — a
   legitimate but different job, judged on completeness rather than on a decision changed. Say which
   before anyone draws. (Convention; long track records, no controlled comparisons.)
4. **Write the arrow contract before drawing, as one legend clause.** *"An arrow means A directly
   causes B"* / *"…sends a message to B"* / *"…precedes B in time"* / *"…is an input to B."* Two
   clauses means two arrow styles and two legend lines, or two diagrams. This matters because adding
   arrows flips readers from a structural reading ("is", "are", naming parts) to a functional and
   causal one ("enters", "opens", "pushes") **whether or not you meant it** — strong experimental
   work, and the finding is about the reader, not the author. If you cannot write the clause you are
   hand-waving, and the picture will still be read as causal. Label arrows with intent ("sends
   settlement file to"), not with a noun ("data"); downgrade the mark when you mean less, since a soft
   association with a hard arrowhead reads as a hard claim; and read each arrow aloud as
   subject-label-object, because reversed ones are audible.
5. **For a formal causal claim, mind the arrows you did not draw.** Under the Greenland–Pearl–Robins
   semantics, X → Y asserts only that X *may* affect Y — weak and barely falsifiable. A **missing**
   arrow asserts there is *no* direct effect, and an omitted node that there is no unmeasured common
   cause. Those absences are the strong, substantive claims, and everything the formalism buys reads
   the blanks. So state whether arrows are **asserted, assumed or estimated**; "arrows are
   assumptions, not findings" is often the most honest line on the page. Visual identity does not
   imply semantic identity: a conceptual DAG and a fitted structural equation model are drawn with the
   same boxes and arrows.
6. **Respect what a feedback picture cannot say.** A causal loop diagram legitimately shows that a
   loop exists, its sign, which loop dominates, and where delays sit. It **cannot** show
   accumulation, magnitude, thresholds or behaviour over time — outside what the notation expresses,
   not details someone forgot. And the field's own review found standard link polarity fails for at
   least one link in most CLDs practitioners draw, because polarity breaks wherever a link crosses a
   stock: reducing the inflow does not reduce the level in the glass. Name every variable as a
   quantity that can go up or down (never an action), mark every delay, check each link against a
   stock, and escalate to a stock-and-flow model the moment the claim concerns magnitude or timing.
   The theory-of-change version of the same test: each arrow carries an assumption *and* a falsifier
   — "we assume trained staff are retained; if turnover exceeds 30 per cent this link breaks."
   Without that you have a funding narrative, and a logic model wearing a theory-of-change label.
7. **Lead a non-expert with one named, concrete, end-to-end scenario** — "a customer disputes a charge
   at 2am" — and offer the structure as the follow-up. Two experimental lines converge: the
   worked-example effect, and the asymmetry that inferring structure from function is easier than
   inferring function from structure, with lower-ability readers specifically disadvantaged. Pick the
   scenario that exercises the contested part, say out loud that it is one path, and name an
   unhappy-path second even if you do not draw it. Use it as a **test** too: walk a real case through
   the structural picture in front of the people who own the parts — where the walk stalls, the
   diagram is lying.

## Required moves

Competent drafters produce a tidy, correct diagram and skip these. Check each:

- [ ] **Which of the three pictures**, stated on the artefact.
- [ ] **The level sentence completed** — "every box here is a ___" — and held.
- [ ] **Pathology named as a sentence** ("orders wait eleven days between credit check and
      fulfilment"), not "understand the process"; form chosen from it, not from house tooling.
- [ ] **Arrow contract written as a legend clause** before the first box, with one style per meaning.
- [ ] **Asserted / assumed / estimated declared**, and for a causal DAG, the absences checked as claims.
- [ ] **Gaps measured, not just steps**, and the boundary stated — an unmeasured queue is the finding
      you came for, left blank, and where the map starts and stops is a claim about whose problem this is.
- [ ] **Escalation named** when the question turns to magnitude, timing or overshoot: that is a
      modelling job, and saying so early is cheaper than saying it after the presentation.

## Failure modes

- **Form chosen before pathology** — the team knows the notation, so the picture is about branching when the argument was about waiting. Invisible from inside, because the diagram is *correct*.
- **Arrows with no defined semantics** — every reader supplies a default, and the modal default is causal. The single most common defect here.
- **Causation implied by a flow** — a data, money or material arrow is a transfer; "the data goes there" becomes "that is why the number moved".
- **Implied sequence from layout** — left-to-right reads as time, so concurrent steps in a row assert an order the layout engine invented.
- **The everything-diagram** — mixed levels, silently approved because each stakeholder recognises their own layer and ignores the rest. Its cousin: the architecture diagram that is really an org chart (rename every box functionally; if it stops making sense, it was one).
- **The hand-waving hairball** — forty variables, no delays, no named loops: unfalsifiable by construction, so any outcome can be narrated from it afterwards.
- **The aspirational theory of change** — boxes widen and outcomes grander to the right; no arrow carries a condition and no box carries a number.
- **The exemplar mistaken for the specification** — one traced path read as "how it always works".
- **The journey map used as delivery diagnosis** — every cause is below the line and off the page, so the remedies land on frontstage staff who did nothing wrong.

## Depth

`representing-information/process-and-causality/one-abstraction-level.md`,
`choosing-a-process-view.md`, `what-an-arrow-claims.md`, `feedback-and-theories-of-change.md` and
`three-pictures-of-one-system.md` in an optional source corpus (when available).
