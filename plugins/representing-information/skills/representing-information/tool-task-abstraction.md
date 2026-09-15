# Task Abstraction

Name *what* the reader is shown and *why*, in vocabulary containing no chart name, before deciding
*how* it is drawn. Munzner's nested model (framework, validated by adoption rather than experiment,
and near-universally accepted) puts four levels in a fixed order — domain situation → data and task
abstraction → visual encoding and interaction idiom → algorithm — and the output of each is the
input to the next.

## The move
- **Write one sentence naming an operation on a target.** Compare, look up, find the extremum,
  characterise a distribution, correlate, detect an anomaly, cluster, browse. Not "make a box plot"
  but "characterise the distribution of settlement time in each of five regions and identify the
  anomalous one."
- **Delete any chart name and see what survives.** If nothing does, you have a request for a
  picture, not a design.
- **Compute the derived attribute.** Half of good design is the right new column — a rate, a
  difference, a residual — not a better encoding of the columns you were handed.
- **Generate a second abstraction on purpose.** Munzner's named failure is treating the first
  framing that arrives as the problem statement.

## The four threats
Each level has one, in her vocabulary: *wrong problem* ("they don't do that") · *wrong abstraction*
("you're showing them the wrong thing") · *wrong encoding* ("the way you show it doesn't work") ·
*wrong algorithm* ("your code is too slow"). Errors **cascade** — an upstream error cannot be
repaired downstream, because the downstream levels optimise faithfully inside a frame that is wrong.
Say which of the four sentences a piece of criticism amounts to before responding to it; a level-2
objection cannot be met with a palette change.

## Apply it — the four-line pre-brief
Before any tool opens (convention, with a framework justification):

- **Question** — ends in a question mark, and names the decision it feeds.
- **Claim** — the sentence you expect to be able to assert.
- **Evidence** — the specific comparison, with its denominator and its uncertainty.
- **Form** — last, and only now.

If the claim sentence cannot be written, you are still in exploratory work and the output is not yet
an artefact for anyone else. Open a chart chooser (Abela, the FT Visual Vocabulary) *after* this, to
generate three candidates — never to terminate the decision.

## Failure modes
- **The beautiful wrong chart** — accurate, fast, well-coloured, answering a question nobody asked.
  It survives review because reviewers also inspect the encoding.
- **First-abstraction lock-in** — every later decision is optimisation inside an unexamined frame.
- **Chart type as requirement** — "we need a Sankey" is an answer to an unstated question.
- **Container as abstraction** — "a dashboard", "a one-pager", "a deck" are occasions, not tasks.
- **Self-validating testing** — a study whose tasks you wrote cannot detect that the tasks were
  wrong. Only target users doing their *own* work can.
- **Debugging the encoding when the abstraction is wrong** — three palette iterations on the wrong
  question. See `tool-when-not-to-draw.md` for the gate order that prevents this.

## Depth
`representing-information/perception-and-encoding/abstraction-before-encoding.md` and
`representing-information/method-and-critique/from-material-to-representation.md` in an optional
source corpus (when available).
