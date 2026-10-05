#!/usr/bin/env node
// Run persona-review.workflow.js without the Workflow tool.
//
// The workflow's agent() calls are answered from files. Each pass runs the
// script from the top: a call whose answer file exists gets that answer; a
// call without one writes its prompt to pending/ and returns null. When
// anything is pending the pass stops before the synthesis and lists the
// prompts to answer. Answer them (one Agent per prompt, in parallel, so the
// reviewers stay blind to one another), then run the same command again.
// When nothing is pending, the result is written to <dir>/result.json.
//
// Because the prompts, the filtering and the tier rule all come from the
// workflow file itself, this path and the Workflow path cannot drift apart.
//
// Usage:
//   node run_offline.mjs <ensemble.json> <run-dir> [--runner agents|in-context] [--workflow <path>]
//
// Exit codes: 0 result written, 3 prompts pending, 1 error.

import { readFileSync, writeFileSync, existsSync, mkdirSync, readdirSync, unlinkSync } from 'node:fs'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const HERE = dirname(fileURLToPath(import.meta.url))
const DEFAULT_WORKFLOW = resolve(HERE, '../../../workflows/persona-review.workflow.js')

function usage(msg) {
  if (msg) console.error(`error: ${msg}`)
  console.error('usage: node run_offline.mjs <ensemble.json> <run-dir> [--runner agents|in-context] [--workflow <path>]')
  process.exit(1)
}

const argv = process.argv.slice(2)
const positional = []
let runner = 'agents'
let workflowPath = DEFAULT_WORKFLOW
for (let i = 0; i < argv.length; i++) {
  if (argv[i] === '--runner') runner = argv[++i]
  else if (argv[i] === '--workflow') workflowPath = resolve(argv[++i])
  else positional.push(argv[i])
}
if (positional.length !== 2) usage('expected an ensemble file and a run directory')
if (!['agents', 'in-context'].includes(runner)) usage('--runner is agents or in-context')

const [ensemblePath, runDir] = positional.map(p => resolve(p))
const answersDir = join(runDir, 'answers')
const pendingDir = join(runDir, 'pending')
mkdirSync(answersDir, { recursive: true })
mkdirSync(pendingDir, { recursive: true })
for (const f of readdirSync(pendingDir)) unlinkSync(join(pendingDir, f))

let ensemble
try {
  ensemble = JSON.parse(readFileSync(ensemblePath, 'utf8'))
} catch (e) {
  usage(`cannot read ${ensemblePath}: ${e.message}`)
}

// ------------------------------------------------- schema check (light) ----
// Enough to catch a malformed answer before it poisons a later stage:
// required keys, primitive types and enums, recursively.
function check(value, schema, path, errors) {
  if (!schema) return
  const t = schema.type
  if (t === 'object') {
    if (!value || typeof value !== 'object' || Array.isArray(value)) { errors.push(`${path}: expected object`); return }
    for (const k of schema.required || []) if (!(k in value)) errors.push(`${path}.${k}: missing`)
    for (const [k, sub] of Object.entries(schema.properties || {})) if (k in value) check(value[k], sub, `${path}.${k}`, errors)
  } else if (t === 'array') {
    if (!Array.isArray(value)) { errors.push(`${path}: expected array`); return }
    value.forEach((v, i) => check(v, schema.items, `${path}[${i}]`, errors))
  } else if (t === 'string') {
    if (typeof value !== 'string') errors.push(`${path}: expected string`)
    else if (schema.enum && !schema.enum.includes(value)) errors.push(`${path}: "${value}" not in ${schema.enum.join('|')}`)
  } else if (t === 'integer') {
    if (!Number.isInteger(value)) errors.push(`${path}: expected integer`)
  } else if (t === 'boolean') {
    if (typeof value !== 'boolean') errors.push(`${path}: expected boolean`)
  }
}

// ---------------------------------------------------------- the hooks ----
const stem = (label) => label.replace(/[^A-Za-z0-9-]+/g, '-')
const pending = []
const invalid = []
class PendingBeforeSynthesis extends Error {}

function pendingPrompt(prompt, opts, answerPath) {
  const schema = opts.schema ? JSON.stringify(opts.schema, null, 2) : null
  return `${prompt}

---

HOW TO RETURN YOUR ANSWER (this run uses files instead of a structured-output tool).
${schema ? 'Your answer is a single JSON object matching this JSON Schema:\n\n```json\n' + schema + '\n```\n' : 'Your answer is plain text.\n'}
Write the answer, and nothing else, to this file with the Write tool. It is the one file you may create:

    ${answerPath}

Then reply with that path and nothing more.
`
}

async function agent(prompt, opts = {}) {
  const label = opts.label || `agent-${pending.length}`
  const name = stem(label)
  const answerPath = join(answersDir, `${name}.json`)
  if (existsSync(answerPath)) {
    const raw = readFileSync(answerPath, 'utf8')
    let value
    try {
      value = opts.schema ? JSON.parse(raw.replace(/^\s*```(?:json)?\s*|\s*```\s*$/g, '')) : raw
    } catch (e) {
      invalid.push(`${name}.json: not valid JSON (${e.message})`)
      return null
    }
    const errors = []
    check(value, opts.schema, name, errors)
    if (errors.length) { invalid.push(...errors.slice(0, 10)); return null }
    return value
  }
  if (opts.phase === 'Synthesize' && (pending.length || invalid.length)) throw new PendingBeforeSynthesis()
  const promptPath = join(pendingDir, `${name}.prompt.md`)
  writeFileSync(promptPath, pendingPrompt(prompt, opts, answerPath))
  pending.push({ label, prompt: promptPath, answer: answerPath })
  return null
}

async function pipeline(items, ...stages) {
  return Promise.all(items.map(async (item, index) => {
    let acc = item
    for (let s = 0; s < stages.length; s++) {
      try {
        acc = await stages[s](s === 0 ? item : acc, item, index)
      } catch (e) {
        if (e instanceof PendingBeforeSynthesis) throw e
        return null
      }
    }
    return acc
  }))
}

async function parallel(thunks) {
  return Promise.all(thunks.map(async t => { try { return await t() } catch (e) { if (e instanceof PendingBeforeSynthesis) throw e; return null } }))
}

const logs = []
// Held back until the run completes: in a pass with prompts pending, the
// workflow's "no review returned" lines describe unanswered prompts, not failures.
const log = (m) => { logs.push(m) }
const phase = () => {}
const budget = { total: null, spent: () => 0, remaining: () => Infinity }
const workflow = () => { throw new Error('nested workflows are not supported offline') }

// ------------------------------------------------------------- run it ----
const source = readFileSync(workflowPath, 'utf8').replace(/^export\s+const\s+meta\s*=/m, 'const meta =')
const AsyncFunction = Object.getPrototypeOf(async function () {}).constructor
const body = new AsyncFunction('args', 'agent', 'pipeline', 'parallel', 'phase', 'log', 'budget', 'workflow', source)

let result
try {
  result = await body(ensemble, agent, pipeline, parallel, phase, log, budget, workflow)
} catch (e) {
  if (!(e instanceof PendingBeforeSynthesis)) { console.error(`error: the workflow threw: ${e.stack || e}`); process.exit(1) }
}

if (invalid.length) {
  console.error('\nAnswers that do not match their schema (fix or delete them, then re-run):')
  for (const m of invalid) console.error(`  ${m}`)
}
if (pending.length) {
  console.log(`\n${pending.length} prompt(s) pending. Give each to its own Agent, all in one message, with:`)
  console.log('  "Your brief is in <prompt file>. Read it and follow it exactly."')
  for (const p of pending) console.log(`  ${p.label}\t${p.prompt}`)
  console.log('Then run this command again.')
  process.exit(3)
}
if (invalid.length) process.exit(1)
if (!result || result.status === 'error') {
  console.error(`error: ${JSON.stringify(result && (result.problems || result.stage))}`)
  if (result) writeFileSync(join(runDir, 'result.json'), JSON.stringify(result, null, 2))
  process.exit(1)
}

for (const m of logs) console.error(`[log] ${m}`)
result.method.runner = runner === 'in-context' ? 'in-context' : 'agent-tool'
result.method.blind = runner !== 'in-context'
result.method.log = logs
writeFileSync(join(runDir, 'result.json'), JSON.stringify(result, null, 2))
console.log(`result written: ${join(runDir, 'result.json')} (status ${result.status})`)
