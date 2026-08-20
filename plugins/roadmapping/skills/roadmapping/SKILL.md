---
name: roadmapping
description: 'Chart, refine and revisit multi-epic technical roadmaps that convey direction, order and known unknowns rather than precision. Use this whenever work spans more than one pull request or epic, when the order of work is not yet decided, when someone asks "what should we build first", "how do we sequence this", "what is the roadmap", or describes a large ambition with vague edges. Reach for this before any planning skill, because work not yet refined into a single ready feature will get false precision from writing-plans. Also use when returning to an existing roadmap to refine a milestone into features, or to check whether reality has overtaken the plan.'
---

# Roadmapping

A roadmap answers three questions: which direction, in what order, and what
we do not yet know. It does not answer how. The moment it starts answering
how, it has stopped being a roadmap and has become a plan that will be
wrong.

This skill exists because planning skills have one resolution setting. Point
them at six months of work and they produce file paths and schemas for things
nobody has looked at yet. Reviewers then correctly attack that precision, and
the whole artefact loses credibility. The fix is not to plan more carefully.
It is to plan at a declared resolution and defend it.

## The evidence rule

This is the core of the skill and everything else follows from it.

**If you do not have hard evidence, you cannot be certain. It is not your job
to obtain that evidence now.**

Both halves matter. The second half is the one that gets ignored. When you
reach a gap, the tempting move is to go and read the code, search the web, or
open five files until you can say something concrete. Do not. That is exactly
how a roadmap fills with confident detail about work nobody has scoped, and it
is the mechanism behind most false precision, not carelessness.

The rule needs a destination, or it just deletes content. So:

**Assert it, or file it as a known unknown. Never research to promote it.**

Every unknown you file gets a *resolved by* pointer: which piece of work,
when finished, will answer it. An unknown without a pointer is a worry. An
unknown with a pointer is structure, and it is the thing that makes the
roadmap worth reading again in three months.

And when nothing planned will answer it, the answer is not to shrug. The
finding out is itself work: file it as a research issue. The evidence rule
defers the research, it does not cancel it. Read *Everything is work* below
before you decide an unknown has no owner.

## The model

Three objects, and each holds exactly one kind of fact.

| Object | Is | Holds |
| --- | --- | --- |
| Milestone | An epic. An idea. | Direction at low resolution, plus an acceptance criterion |
| Issue in a milestone | A feature, a refinement, or a research spike | Executable work, at whatever resolution it has earned |
| Index document, in repo | The argument | Why this direction, why this order, what we do not know |

**A milestone whose only open issue is its refinement issue is only an idea,
and is not executable.** No agent may start building from a milestone or from
the index. Work starts from a refined feature or it does not start. This is
the anti-precision rule expressed as a data shape rather than a plea, and it
is more reliable than any amount of prose telling you to stay vague.

### The refinement issue

Every milestone carries at least one issue from the moment it is created: an
issue that says this milestone must be refined.

It is there for four reasons.

- GitHub treats a milestone as complete when its issue list empties, so a
  milestone with no issues at all reports a completeness it has not earned. A
  refinement issue makes an unrefined milestone honestly read as 0 of 1.
- It is the executable representative of an idea. It is the only thing you can
  honestly commit to doing about an unrefined milestone: look at it and
  decide. That means direction-level ordering can be expressed structurally,
  as dependencies between refinement issues and the features that must exist
  before shaping is even sensible, without inventing any detail.
- An agent looking for work in an unrefined milestone finds only "refine
  this", so the executability rule enforces itself.
- Its definition of done is the coverage check: features exist that plausibly
  satisfy the milestone's acceptance criterion.

Two rules keep it from rotting.

**It is a task, not a container.** Its body is a pointer to the index entry
and the acceptance criterion, and nothing else. Write the epic into it and you
have recreated the duplicate-source problem the index was meant to solve.

**Close it when refinement completes.** Re-refining later is a new issue,
which leaves a visible trail of how often this milestone was rethought.
That trail is useful signal about where the real uncertainty sits.

Resolution is therefore derived, never stored:

- milestone whose only open issue is its refinement issue → **direction**
- milestone with feature issues, not yet ready → **refined**
- issue marked ready → hand off, no longer this skill's business

Do not add a resolution field. Compute it. A stored value drifts; the graph
does not.

### Everything is work

Refinement is work. Research is work. Both cost time, both can be blocked,
both can be done badly or skipped, and neither is visible to anyone if it
lives only in a document. So both get issues, in the same tracker as delivery
work, ordered by the same dependencies.

Three kinds of issue, distinguished by type or label:

| Kind | Done when | Produces |
| --- | --- | --- |
| Research | The question is answered | Evidence |
| Refinement | Features exist that cover the acceptance criterion | Features |
| Feature | The software works | Software |

This is what makes the evidence rule honest. "It is not your job to obtain
that evidence now" would be avoidance if the obtaining vanished. It does not
vanish; it becomes a research issue with an owner, a place in the queue, and
a blocking relationship to whatever needs the answer.

It also makes the information-gain argument executable rather than rhetorical.
"We should do X first because it resolves Y's biggest unknown" stops being a
sentence in a document and becomes a research issue that blocks `refine Y`.

**Research issues carry an appetite.** How much time this is worth, decided
before starting. A spike without one is the fact-stuffing failure with a
ticket number attached: an agent researching until it feels confident. If the
appetite is exceeded, that is a finding in itself, usually that the area is
harder than the direction assumed, and it belongs in the index as a possible
change of direction rather than as a request for more time.

**Closing a research issue updates the index.** Its output is evidence, so
items that were `derived` may now be `evidenced` or now be wrong. A spike
whose answer never reaches the argument was wasted.

**Do not ticket every unknown.** This is the counterweight, and without it the
principle floods the tracker with planning work and drowns the delivery
signal. The test is whether not knowing changes what you do next. If it does,
it is a research issue. If it does not, it is a recorded unknown, and
recording it is enough.

### Where research output lives

A spike produces three different things with three different lifetimes, and
the question only feels hard because they get treated as one artefact.

**The working** stays in the research issue, as comments. Benchmarks, notes,
dead ends, the data. It is a work log: append-only, timestamped, already
attached to the unit of work, and rarely read again. It does not belong in
the repo. Never create a per-spike document; that is how you end up with the
parallel-document sprawl that nobody reads.

**The verdict** goes in the issue's closing comment, in a few lines, so the
issue is self-contained and answerable later with a single `gh issue view`.

**The consequence** goes in the index, because the index holds the argument
and a spike that changes the argument must change it. This is not optional:
a research issue that closes without moving the argument produced nothing.

Then understand why the split falls where it does, because the instinct to
promote an important finding into the repo too early is strong, and the
instinct to leave it in the tracker forever is worse.

**The tracker is working memory. The repo is the record.** Everything in
issues and milestones is eventually ephemeral: it gets closed, compacted,
archived, migrated, and nobody treats a three-year-old issue thread as
authoritative. What went through commit, pull request, review and merge is
fixed. Review is the gate that turns a note into a fact of the project.

Research is therefore ephemeral by nature. It is provisional, unreviewed, and
aimed at work that does not exist yet. The issue is the right home for it
while that is true.

**When the work lands, the finding stops being research.** It is now either
true of the codebase or it was wrong. So at the point a feature merges, ask
the question that closes the loop:

> What did the spike teach that the code does not now show?

- Nothing: the finding is fully embodied in the code and its tests. The issue
  can decay. This is the best outcome.
- Something a reader would need and cannot infer: commit it as documentation,
  through the same review as the code. It is maintained from then on, because
  changing the code without changing it is a reviewable omission.
- The finding killed a direction, so no feature will ever embody it: that is a
  decision, and it belongs in whatever the project uses to record decisions,
  committed and reviewed like anything else.

Anything still living only in an issue after the work landed is, by
definition, not yet a fact of the project. Treat that as unfinished work
rather than as an archive.

This also means `evidenced` locators need repointing. A claim in the index
whose only locator is a spike issue is on borrowed time. Once the work merges,
point it at the code, the test, or the committed document instead.

The index itself is not an exception to any of this. It lives in the repo and
goes through review, which is precisely why it is allowed to hold the
argument. It still carries a link rather than a restated finding, so that the
number decays where its owner can see it rather than inside the one document
you wanted to keep low-churn.

### Milestone acceptance

Every milestone carries an acceptance criterion, written at charting time,
before any feature exists.

This is not bureaucracy. Refinement decomposes intent into features, and
decomposition is lossy. GitHub closes a milestone when its issues are closed,
which tells you the list is finished, not that the intent is met. Without a
criterion fixed in advance, "all issues closed" gets read as "epic delivered"
and nobody notices the gap between what was wanted and what was built.

Write it as an outcome, not a specification: what becomes true for someone
once this milestone is real. Outcomes are writable without evidence, which is
precisely why they belong at direction resolution, where specifications do
not.

**Freeze it through refinement.** The criterion is the independent check on
the decomposition, so rewriting it to match the features you happened to
create destroys the only thing it was for. If it turns out to be unachievable
or wrong, that is a change of direction: record it as one, with the reason,
in the index.

A milestone closes when its criterion is met, not when its issue count
reaches zero.

### Where order lives

Order lives in two places that never make the same claim, so they cannot
contradict each other by accident:

- **The graph** orders executable work, through GitHub issue dependencies
  (`gh issue create --blocked-by`, `gh issue edit --add-blocked-by`, and
  `is:blocked` to find bottlenecks). Refinement issues are executable, so
  direction-level ordering lives here too: mark `refine B` as blocked by the
  feature in A that must exist before B can sensibly be shaped. That is the
  information-gain argument made structural, with no invented detail.
- **The index** argues about ideas, at a resolution the graph cannot carry:
  why this direction, why we lean this way, what we do not know.

Encode only the edge that carries information. `refine B` blocked by
`feature X in A` says something. A feature in B blocked by `refine B` is
tautological, since features in B do not exist until refinement is done, and
filling the graph with tautologies makes the real edges harder to see.

Give refinement issues their own issue type or label. Otherwise `is:blocked`
and every dependency count mixes planning work with delivery work, and the
health signal you wanted from the graph gets diluted.

Milestones are never truly independent, but the dependency almost always sits
in a feature beneath the milestone, not at milestone level. So do not try to
order milestones structurally.

**Never set a milestone due date.** It is the only ordinal GitHub offers, and
using it silently converts a set of intentions into a schedule. Milestones can
arrive sooner, get postponed, or run in parallel with features woven between
them. A total order is a claim you do not have evidence for.

### What the index must not hold

The index carries direction, the ordering argument, and milestone-level
unknowns. It never carries state: no percentages, no open/closed counts, no
in-flight lists. State belongs to GitHub, which already tracks it correctly
and for free. An index that tracks state churns constantly, conflicts on
merge, and goes stale invisibly. An index that carries only argument changes
when the thinking changes, which is the only diff worth reading.

## Provenance

A roadmap is agent synthesis. Left unmarked, it reads next session as settled
user intent, and you end up citing the user's own words back at them from a
document they never wrote. Tag every item:

- `stated` — the user said it.
- `derived` — your synthesis.
- `evidenced` — read from code or repo, with the locator.

The tag records **who owns the item, not who is right**. Users are wrong
sometimes, so everything here is challengeable. What differs is the mode:

- `derived` — revise it in place at any refinement. It was yours to begin
  with, and quietly correcting your own earlier synthesis is the job.
- `stated` — never revise unilaterally. If evidence contradicts it, surface
  the contradiction and let the user decide. Silently complying with a
  premise you have found to be false is the same miscalibration as inventing
  detail, pointed the other way.
- `evidenced` — re-check the locator on revisit. Code moves, and an
  `evidenced` claim whose locator no longer resolves is now `derived`.

**Default to `derived` for anything you generate.** This is what makes the
evidence rule enforceable later rather than only at creation, because
refinement can reopen every `derived` item without argument.

The index gets a header saying it is agent-authored synthesis, not a record of
decisions. Anything you post to GitHub carries the operator's attribution
signature; check the user's agent instructions for the exact required wording
and reproduce it verbatim rather than paraphrasing it.

## Recording the medium

The roadmap must still be findable in six months, by an agent that has none of
this conversation. On first use, establish and record:

- where the index lives (repo path)
- where milestones live (repo, or org-level project)
- the pointer stanza written into `CLAUDE.md` / `AGENTS.md`

The stanza contains a **pointer, never content**. Content in an instruction
file goes stale without anyone noticing. Something like: the roadmap index is
at `<path>`, milestones are in `<repo>`, read the index before planning work
here, update it when direction changes.

Link bidirectionally: the index links to each milestone URL, each milestone
description links back to the index path. An agent should never have to guess
which document applies.

## Charting a roadmap

1. Establish the ambition and the constraints from the user. Ask; do not
   infer. Anything you infer is `derived` and must be marked so.
2. Propose milestones as areas of intent. Descriptions stay short. If you
   cannot describe a milestone without naming files or schemas, the milestone
   is too small and is probably a feature.
3. Write each milestone's acceptance criterion now, as an outcome, while no
   features exist to bias it.
4. For each milestone, name the unknowns. What would we need to learn before
   this is even shapeable? Give each a resolved-by pointer. Where nothing
   planned resolves one and not knowing changes what you do next, create a
   research issue with an appetite and point at that.
5. Argue the order. The useful argument is **information gain**: we lean
   towards X before Y because X cheaply resolves Y's largest unknown. Order
   justified only by dependency is a Gantt chart; order justified by what it
   teaches you is a roadmap.
6. Write the index. Create the milestones, each with its refinement issue
   and nothing else. Create no feature issues.

## Refining a milestone

Refinement turns a milestone description into a set of feature issues that
start as not ready. This is ordinary agile refinement, not a novel ceremony,
and calling it what it is helps reviewers know what they are looking at.

This is where the evidence rule is under most pressure, because you now have
to say something concrete per feature. Hold the line: features may be
incomplete and marked not ready. They may not be invented.

- Use the repository's issue template if one exists. Read it first. Note that
  issue forms are enforced in the web UI only and are bypassed by
  `gh issue create`, so treat the template as a convention you follow
  deliberately, and never assume the fields are present when reading back.
- Set dependencies as you go, with `--blocked-by`.
- **Check for blockers outside this milestone.** This is the single most
  commonly missed step, because you are looking at one milestone while the
  blocker sits in another. Weaving across milestones is normal and expected.
- **Check coverage against the acceptance criterion.** Would every feature
  here closing actually satisfy it? Decomposition loses things quietly, and
  this is the only moment the loss is cheap to spot. If there is a gap, add a
  feature or record the shortfall; do not edit the criterion to fit.
- Close the refinement issue only once that coverage check holds.
- Refinement may contradict the direction: you discover a feature here that
  blocks a feature in an already-refined milestone. This is not a failure, it
  is evidence overturning direction, and it is the event the roadmap exists to
  surface. The graph wins. Rewrite the argument in the index; never bend the
  graph to match the prose.

Then run the review in `references/refinement-review.md` before finishing.

## Revisiting

A roadmap that is not maintained is worse than none, because it is confidently
wrong. On revisit:

- What closed, and which unknowns did it resolve?
- Does the graph now contradict the ordering argument?
- Did anything get postponed, and why? Record the reason: an unknown got
  worse, or something else became more valuable. A roadmap whose history you
  cannot read is one you cannot trust.
- Which `derived` items are now `evidenced`, or now wrong? Every closed
  research issue should have moved something here.
- Did any research issue exceed its appetite? That is a finding about the
  direction, not a request for more time.
- For any milestone whose issues are all closed: is its acceptance criterion
  actually met? An empty issue list is not delivery.
- Does any evidence now contradict a `stated` item? Surface it; do not edit
  around it.

Update the argument. Do not rewrite history; note what changed and why.

## Handing off

When exactly one feature becomes next and is marked ready, this skill is
finished. Stop, and invoke `superpowers:brainstorming`, then
`superpowers:writing-plans`. Those skills are correct for a single unit of
work and this one is not. Do not try to be the whole methodology.

Equally, do not accept work this skill should not do. A defect, or something
that is wrong and needs investigating, is not roadmap work; that is what the
`github-issues:writing-issues` skill is for.

## Stop rules

At **direction** resolution, refuse to write, and say which rule you are
applying:

- file paths, module names, API signatures, schema fields
- test scenarios, or acceptance criteria at feature level (the milestone's
  outcome-level criterion is required and is a different object)
- week numbers, dates, effort in hours or points
- pinned library or tool versions
- any claim you would have to go and research in order to make

At any resolution, refuse:

- an unknown with no resolved-by pointer, no research issue, and no note
  that not knowing it changes nothing
- a research issue with no appetite
- an ordering claim with no argument attached
- an untagged item, or a `stated` tag on something the user did not say
- state written into the index
- a milestone due date
- a milestone with no acceptance criterion, or a criterion edited during
  refinement to match the features that now exist
- a milestone with no refinement issue, or a refinement issue carrying the
  epic body rather than a pointer to the index

Name the violation and give the concrete fix. Do not soften it to be
agreeable; the entire value of the artefact is that its confidence is
calibrated.
