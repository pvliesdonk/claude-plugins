# Domain Models, Ontologies and Taxonomies

The request arrives as "here is our ontology, can you make it presentable". Taken literally it is the
wrong request, and answering it literally produces the artefact everyone has seen: a wall of boxes, a
legend longer than the decision, a room that nods and does not engage. **The whole model is not an
artefact. It is a source from which artefacts are cut.** Completeness feels like the achievement,
which is exactly why it is the thing to give up first.

## The recipe

1. **Name the question in task vocabulary.** Adjacency ("what connects to this?"), accessibility
   ("can A reach B?"), common connection, attribute lookup or ranking, browsing ("where does this
   sit?"), overview estimation ("how many, how dense?"). Not "understand the model" — that names a
   feeling. Surveys of ontology tooling find it usually remains vague which task a visualisation
   supports, so the habit is endemic rather than personal; a picture that supports every task
   supports none. Then check the cheap answer: an overview task is a number in a sentence, a ranking
   is a sorted list, adjacency for one class is two columns. A surprising share of these requests
   resolve that way (`choosing.md`, `tool-task-abstraction.md`).
2. **Decide specification or argument, out loud.** A specification is consumed by people who share a
   notation and must be correct. An argument is aimed at people whose agreement you need. One
   artefact cannot be both; the attempt is too detailed to read and too vague to implement.
3. **Pick the exemplar vignette before anything is drawn.** One realistic case followed end to end
   through the classes it touches — one claim from submission to payment, one sensor reading from
   capture to alert. Keep the complete model as an appendix, a browsable tool or a file. Highest-value
   move here, and the one most reliably skipped.
4. **Separate schema from instances.** Show the schema as structure; show instances as *data* —
   tables, facets, counts, or a few exemplar individuals on a fragment of the schema. Where the two
   must meet, encode population as a node *attribute*, not as extra nodes. VOWL's authors dropped
   their integrated T-box/A-box view after user study on scalability grounds — a six-participant
   think-aloud study whose influence far exceeds its evidence, though the failure it names is a
   category error rather than a layout problem: the twelve-class demo collapses on real data because
   every instance became a node.
5. **Let the question choose the form**, not the tooling default:

   | The audience's question | Form |
   |---|---|
   | "How does A connect to B?", trace this chain — small, sparse graph | Node-link |
   | "Which concepts are most connected?", counting, ranking, clusters | Adjacency matrix (ordered, not alphabetical), or a sorted bar chart |
   | "Where does this sit?", "what is a kind of what?", depth | **Indented list** with search and collapse |
   | "How much data sits in each branch?" | Treemap — only if a real size attribute exists |

   Above roughly twenty nodes matrices beat node-link diagrams on most tasks, and only path finding
   consistently favours node-link — a preference that itself reverses on large dense graphs. That
   result is experimental and replicated; but treat twenty as a floor, since the study's sparsest
   graphs are denser than most hand-built taxonomies, which pushes the crossover later for curated
   models. **The uncomfortable finding:** over a 205-class ontology, a plain indented class browser
   beat four graphical visualisations on both time (about 74 seconds against 94, 97 and 190) and
   correctness (95% against roughly 88%, 88% and 78%). One study, one ontology, one task family,
   tools since discontinued — but it is the most useful thing to put in front of anyone insisting
   their taxonomy needs a diagram, and the list's advantages are structural: searchable, collapsible,
   screen-readable, diffable, copy-pasteable.
6. **Run the leave-it-out list, in order.** (a) Anything that cannot help answer the named question.
   (b) The instances. (c) Everything below the top two or three levels — depth is list territory.
   (d) `owl:Thing`, reified plumbing, upper-ontology scaffolding, anything named `*Abstract*`, unless
   the audience maintains it. (e) Full expressivity — restrictions, cardinalities, unions — for any
   audience that is not logicians. Keep leaf detail in exactly one place, the vignette. Then
   **caption what you removed and on what rule**: the step that turns a reduction into an argument
   rather than a misrepresentation.
7. **Cut to the audience. Never the same artefact twice.**

   | Audience | Needs | Rejects | Give them |
   |---|---|---|---|
   | **Domain experts** | Their vocabulary; propositions they can disagree with; edge cases | Formal notation, abstract superclasses, anything named after a standard | Labelled propositions over a vignette, plus a terms-and-definitions table. Ask them to **correct**, not approve |
   | **Engineers** | Cardinality, identity, keys, nullability, cascade behaviour, naming | Hand-wavy boxes without multiplicities; pictures they cannot diff or generate from | A formal class or entity-relationship diagram, or the textual schema, generated from the source of truth |
   | **Executives** | Five to nine blocks, the decision at stake, cost or risk framing | Anything needing a legend; anything unreadable in twenty seconds | Named subdomain blocks, one-line captions, no crossings — and consider no diagram: a three-row table often wins |
   | **Newcomers** | A worked example, a glossary, a sense of shape | The full hairball; an alphabetical class list | One vignette path plus a searchable indented hierarchy — better, have them build their own map |

8. **Ask domain experts to correct, not approve.** "Does this look right?" buys a yes that validates
   the labels and misses the semantics — a signed-off misunderstanding. Ask them to state the
   propositions in their own words, then check your formalisation against their sentences. If the
   goal is that they *learn* the domain, have them build the map rather than read yours: the evidence
   here is genuinely strong — two meta-analyses, with constructing (g = 0.72) clearly beating
   studying (g = 0.43).

## Required moves

Capable practitioners draw a tidy diagram and skip all of these. Check each:

- [ ] **Question named as a task**, in writing, before any tool is opened — and put in the caption.
- [ ] **Cheap-form check run** — sentence, sorted list or two-column table ruled out explicitly.
- [ ] **A vignette chosen, and the whole model refused.** The complete model is an appendix.
- [ ] **Schema and instances split** into different pictures, population as an attribute.
- [ ] **Form chosen from the question**, not from the tool's default force-directed layout.
- [ ] **Leave-it-out list run in order, and what was cut said out loud** in one caption sentence.
- [ ] **Specification or argument declared** — and only that one built.
- [ ] **Experts asked to correct**; every edge in an elicitation artefact carries a linking phrase,
      because an unlabelled arrow is an unrecorded disagreement.
- [ ] **Formal notation treated as an audience filter.** UML, ER and ArchiMate carry information a
      reader recovers only by knowing the notation, and Moody's analysis finds such notations violate
      graphic economy and perceptual discriminability (influential, partly contested — later work
      found no advantage for notation improvements in model *construction*). Precision that excludes
      the audience you need is not precision.

## Failure modes

- **The wall chart** — the complete model at a steering committee: too detailed to read, too abstract to act on.
- **The toy-model demo** — magical on twelve classes, collapsed on real data, because every instance became a node.
- **The unquestioned diagram** — produced without a named question, then defended on the grounds that it shows everything. Completeness is not a task.
- **Force-directed by default** — a node-link reflex, when the real question was counting or ranking.
- **The mirror failure** — handing executives a matrix when they wanted one story-path through the model.
- **The unsized treemap** — rectangles sized by node count or label length; readers extract magnitude from area whether or not you meant it.
- **Flattening a graph into a tree** to get a clean picture, silently discarding the extra parents.
- **Layout as displacement activity** — a week tuning parameters on a four-hundred-class model. Readability work cannot help at that size; reduction can.
- **Approval theatre** — a yes from a domain expert treated as validation of the semantics.

## Depth

`representing-information/structures-and-relationships/presenting-an-ontology.md` in an optional
source corpus (when available), with `node-link-versus-matrix.md`, `hierarchies.md`,
`reducing-a-large-graph.md`, `naming-the-question-first.md` and `concept-maps.md` in the same cluster.
