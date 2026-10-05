# The ensemble file

`ensemble.json` is the whole input to a review. The workflow validates it
before dispatching anything and returns every problem at once.

## Document fields

| Field | Required | Who sees it | What it holds |
|-------|----------|-------------|---------------|
| `title` | yes | all | The document's name. |
| `date` | yes | all | `YYYY-MM-DD`. A workflow cannot read the clock. |
| `pin` | no | report | The version reviewed: commit SHA, or date plus file hash. |
| `back_cover` | yes | all | What a reader knows before opening it: one to three sentences, as a cover, a listing or a link preview would say it. |
| `seat` | no | all | When and where it is read ("on publication in November 2026", "from a search result"). Dates are judged from here. |
| `reader_files` | yes | all | Paths or globs, relative to the project root, of what a reader gets. |
| `withheld` | no | readers, as a do-not-open list | Authors' internals: notes, conventions, drafts. |
| `format_notes` | no | readers, editors | How to read source artefacts: "YAML frontmatter and `[@key]` markers are source format; read past them". |
| `design_context` | no | verifiers, synthesis | Deliberate design decisions, so friction with them is reported as a collision, not dismissed. |
| `intended_takeaways` | no | verifiers, synthesis | What a reader must leave with. Each teach-back is checked against these. |
| `ground_truth` | no | verifiers | What the document describes or relies on: source code, a fact register, cited sources. Beats a reviewer's recall. |
| `done_when` | no | synthesis | Acceptance criteria the synthesis measures clause by clause. |
| `drafted_with_ai` | no | report | `true` adds the caveat that same-family reviewers under-flag model-written text. |
| `previous` | no | synthesis | `{ "date", "pin", "priorities": [titles] }` from the last round. |
| `model`, `verify_model` | no | runner | A model tier for every agent, or for the verifiers only. Omit both to inherit the session's. |
| `max_verify_per_reviewer` | no | runner | Default 10. Findings over the cap stay, marked unverified, and the run log says how many. |

## Persona fields

| Field | Required | What it holds |
|-------|----------|---------------|
| `key` | yes | Lowercase, digits, hyphens; unique across personas and lenses. |
| `label` | yes | The heading in the report. |
| `tier` | yes | `primary` (the document exists for them), `gatekeeper` (decides acceptance, funding, publication or purchase), `secondary` (also reads it), `adversarial` (reads for the weakest point). |
| `brief` | yes | Who they are, in the second person: role, situation, prior knowledge, what they distrust, how they read. |
| `goal` | yes | What they are trying to do or decide. |
| `entry` | yes | Where they start: a file, a section, a search result, `llms.txt`. |
| `stop_when` | yes | The condition that ends the walk, reachable by reading: "you can name the command you would run", "a go/no-go", "you would put it down". |
| `came_for` | yes | Two to five expectations, written from their situation before anyone reads the document. For a gatekeeper scoring against a call or a rubric, list the criteria here. |
| `budget_words` | no | Reading patience in words. |
| `coverage` | no | `path` (default): findings cover the walk only. `whole`: after the walk, read the rest and mark findings past the stop point. |
| `weighting` | no | How this reader trades reading experience against correctness: "70% experience, 30% correctness". |
| `reader_files` | no | Overrides the document's, for a reader who gets something else (an LLM client reading `llms.txt`). |
| `source` | no | `author` (the author named this reader), `evidence` (real reader data), `inferred` or `assumed`. Shown in the confirmation table. |

## Lens fields

`key`, `label` and `brief` as above, and `rubrics`: the files the editor reads
first. A lens without a rubric judges taste, so give it one: the project's
style guide, a conventions file, an installed style skill's file, or the call
text for a compliance lens.

## Writing a card

- Goals, stakes, prior knowledge and reading habits change what a reader
  notices; age, gender and nationality rarely do. Keep only attributes that
  change the reading.
- Make the brief concrete enough to decide a case: "has never run an MCP
  server" beats "non-technical"; "signs the declaration that puts the product
  on the market" beats "senior".
- Write `came_for` before reading the document closely. Expectations written
  after reading drift towards what the document happens to deliver.
- Budgets: about 200 words a minute for careful reading, 300 for skimming. A
  five-minute evaluator is 1,000 words. For an LLM client, convert its token
  budget at about 0.75 words a token.
- Use `coverage: whole` for a document read cover to cover (a handbook, a
  paper); `path` for one consulted (a docs site, a reference).
- For an adversarial reader, require a fair restatement of the argument
  before any objection, and for each objection the evidence that would
  answer it.
- Mark a card `assumed` when no one has told you this reader exists, and say
  so in the confirmation table.

## Example

```json
{
  "title": "Widget Sync documentation",
  "date": "2026-10-05",
  "pin": "3f2a9c1",
  "back_cover": "The documentation site of Widget Sync, an open-source tool that copies notes between devices.",
  "seat": "Arriving from a search result in October 2026.",
  "reader_files": ["README.md", "docs/**/*.md"],
  "withheld": ["docs/design/", "AGENTS.md"],
  "ground_truth": ["src/"],
  "design_context": "Tutorials and deployment pages are deliberately separate; each concept has one home page and others link to it.",
  "intended_takeaways": ["A laptop install must set SYNC_DIR"],
  "done_when": ["No primary reader ends the walk misled"],
  "personas": [
    {
      "key": "evaluator", "label": "Evaluator", "tier": "gatekeeper",
      "brief": "You found this in a list of sync tools. You use Syncthing today and have five minutes.",
      "goal": "Decide whether to try it instead.",
      "entry": "README.md",
      "stop_when": "You have a go or no-go and its reasons.",
      "budget_words": 1000, "coverage": "path",
      "came_for": ["What it does that Syncthing does not", "What it costs to run", "Whether it touches my files"],
      "source": "author"
    }
  ],
  "lenses": [
    {
      "key": "style", "label": "Plain-language editor",
      "brief": "Check sentence length, front-loading and headings against the house style.",
      "rubrics": ["docs/STYLE.md"]
    }
  ]
}
```
