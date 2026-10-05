#!/usr/bin/env python3
"""Render a persona-review result as a markdown report, with three checks.

Usage:
    python3 render_report.py ENSEMBLE.json RESULT.json [-o REPORT.md]
                             [--previous PREVIOUS_RESULT.json] [--root DIR]

RESULT.json is the object the workflow returns, or the file run_offline.mjs
writes. A background-task wrapper whose `result` field holds the object, as a
JSON string or parsed, is accepted too.

The checks are deterministic and run on every render:

* Quotes. Every kept finding's quote is searched for in the document's
  reader files, after normalising whitespace, typographic quotes, dashes
  and inline markup. A quote that is not found is flagged in the finding and
  listed under Method; it is not dropped, because the verifier already
  dropped the ones it could not find and a miss here may be a markup
  artefact. Read it before acting on the finding.
* Reading cost. Each walk's path is summed in words (whole files, or
  `file#Heading` sections) and set against the persona's budget_words.
* Previous round. With --previous, the counts per reader are compared, and
  each previous finding's quote is searched for in the current document:
  a surviving quote means surviving text, not necessarily a surviving
  problem.

Every path argument must resolve to somewhere under the working directory,
and files are read only from under --root (default: the working directory).
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
from pathlib import Path

SEV_ORDER = {"blocker": 0, "major": 1, "minor": 2}
TIER_ORDER = {"primary": 0, "gatekeeper": 1, "secondary": 2, "adversarial": 3, None: 4}


# ------------------------------------------------------------- loading ----

def under_cwd(name: str) -> Path:
    """Resolve a path argument, refusing one outside the working directory."""
    root = Path.cwd().resolve()
    path = (root / name).resolve()
    if path != root and root not in path.parents:
        raise SystemExit(f"error: {name!r} is outside the working directory {root}")
    return path


def load_json(path: Path):
    with path.open(encoding="utf-8") as fh:
        data = json.load(fh)
    if isinstance(data, dict) and "reviews" not in data and "result" in data:
        data = data["result"]
        if isinstance(data, str):
            data = json.loads(data)
    return data


def resolve_files(patterns: list[str], root: Path) -> dict[str, str]:
    """Map relative path -> text for every file the patterns match under root."""
    texts: dict[str, str] = {}
    root = root.resolve()
    for pattern in patterns:
        for hit in sorted(glob.glob(str(root / pattern), recursive=True)):
            path = Path(hit).resolve()
            if root not in path.parents and path != root:
                print(f"warning: {pattern} matches {path}, outside {root}; skipped", file=sys.stderr)
                continue
            if path.is_file():
                rel = str(path.relative_to(root))
                try:
                    texts[rel] = path.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    print(f"warning: {rel} is not UTF-8 text; skipped", file=sys.stderr)
    return texts


# -------------------------------------------------------------- quotes ----

_QUOTES = str.maketrans({"\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"',
                         "\u2013": "-", "\u2014": "-", "\u00a0": " ", "\u2026": "..."})


def normalise(text: str) -> str:
    text = text.translate(_QUOTES)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)  # [label](url) -> label
    text = re.sub(r"[*_`>#|]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()


def quote_found(quote: str, corpus: str) -> bool:
    q = normalise(quote).strip(" .\"'")
    if not q:
        return False
    if q in corpus:
        return True
    # A quote elided with "..." is found if every part of it is.
    parts = [p.strip(" .\"'") for p in q.split("...")]
    parts = [p for p in parts if len(p) >= 12]
    return len(parts) > 1 and all(p in corpus for p in parts)


# --------------------------------------------------------------- words ----

def words(text: str) -> int:
    return len(re.findall(r"\b\w[\w'-]*\b", text))


def section(text: str, heading: str) -> str | None:
    """The text under a markdown heading, up to the next heading of the same or higher level."""
    want = normalise(heading)
    lines = text.splitlines()
    for i, line in enumerate(lines):
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m and normalise(m.group(2).rstrip().rstrip("#")) == want:
            level = len(m.group(1))
            out = []
            for nxt in lines[i + 1:]:
                n = re.match(r"^(#{1,6})\s", nxt)
                if n and len(n.group(1)) <= level:
                    break
                out.append(nxt)
            return "\n".join(out)
    return None


def path_words(path: list[dict], texts: dict[str, str]) -> tuple[int, list[str]]:
    """Sum the words of each location on a walk; return the total and the locations not counted."""
    total, uncounted, seen = 0, [], set()
    for step in path or []:
        loc = (step.get("location") or "").strip()
        file_part, _, heading = loc.partition("#")
        file_part = re.sub(r":\d+(-\d+)?$", "", file_part.strip())
        key = (file_part, heading.strip())
        if key in seen:
            continue
        seen.add(key)
        text = texts.get(file_part)
        if text is None:
            uncounted.append(loc)
            continue
        if heading:
            sect = section(text, heading)
            if sect is None:
                uncounted.append(loc)
                continue
            total += words(sect)
        else:
            total += words(text)
    return total, uncounted


# ----------------------------------------------------------- rendering ----

def label_map(result: dict) -> dict[str, str]:
    labels = {}
    for r in result.get("reviews", []):
        labels[r["key"]] = r.get("label") or r["key"]
    counts: dict[str, int] = {}
    for v in labels.values():
        counts[v] = counts.get(v, 0) + 1
    return {k: (f"{v} ({k})" if counts[v] > 1 else v) for k, v in labels.items()}


def names(keys, labels) -> str:
    return ", ".join(labels.get(k, k) for k in keys or [])


def tally(findings) -> str:
    c = {"blocker": 0, "major": 0, "minor": 0}
    for f in findings:
        c[f.get("severity", "minor")] = c.get(f.get("severity", "minor"), 0) + 1
    return f"{c['blocker']} / {c['major']} / {c['minor']}"


def cell(text) -> str:
    return str(text if text is not None else "").replace("|", "\\|").replace("\n", " ")


def build(ensemble: dict, result: dict, texts: dict[str, str], previous: dict | None,
          prev_texts_note: str | None) -> tuple[str, dict]:
    syn = result.get("synthesis") or {}
    reviews = result.get("reviews", [])
    labels = label_map(result)
    corpus = normalise("\n".join(texts.values()))
    stats = {"quotes_checked": 0, "quotes_missing": []}

    for r in reviews:
        for f in r.get("findings", []):
            stats["quotes_checked"] += 1
            f["_quote_ok"] = quote_found(f.get("quote", ""), corpus) if texts else None
            if f["_quote_ok"] is False:
                stats["quotes_missing"].append((r["key"], f.get("location", "")))

    out: list[str] = []
    w = out.append
    method = result.get("method", {})

    w(f"# Persona review: {result.get('title') or ensemble.get('title')}")
    w("")
    pin = result.get("pin") or ensemble.get("pin")
    n_readers = len([r for r in reviews if r.get("kind") == "persona"])
    n_lenses = len([r for r in reviews if r.get("kind") == "lens"])
    w(f"Reviewed {result.get('date', '')}{f' at {pin}' if pin else ''}. "
      f"{n_readers} simulated reader{'s' if n_readers != 1 else ''} and "
      f"{n_lenses} editor lens{'es' if n_lenses != 1 else ''}. "
      "The readers are a model playing people, so every finding about how a reader reacts is a "
      "prediction to test, not an observation; see *Method and caveats*.")
    w("")
    if result.get("status") != "ok":
        w(f"**Run status: {result.get('status')}.** No review came back from: "
          f"{names(method.get('failed'), labels) or 'none'}.")
        w("")

    w("## Summary")
    w("")
    w(syn.get("summary", "(no synthesis)"))
    w("")

    if syn.get("priorities"):
        w("## Priorities")
        w("")
        for i, p in enumerate(syn["priorities"], 1):
            w(f"### {i}. {p['title']}")
            w("")
            w(p["rationale"])
            w("")
            w(f"Raised by: {names(p.get('raised_by'), labels)}. Where: {'; '.join(p.get('locations') or [])}.")
            w("")

    if syn.get("conflicts"):
        w("## Decisions for the author")
        w("")
        w("Readers who want opposite things, or reader friction that collides with a design decision. "
          "The reviews cannot settle these.")
        w("")
        for i, c in enumerate(syn["conflicts"], 1):
            kind = "Readers disagree" if c.get("kind") == "readers-disagree" else "Design collision"
            w(f"{i}. **{kind}.** {c['description']}")
            w(f"   - Between: {names(c.get('between'), labels)}.")
            for o in c.get("options") or []:
                w(f"   - Option: {o}")
            if c.get("settle_by"):
                w(f"   - Settled by: {c['settle_by']}")
            w("")

    if syn.get("done_when"):
        w("## Done when, measured")
        w("")
        w("| Criterion | Result | Evidence |")
        w("|---|---|---|")
        for d in syn["done_when"]:
            w(f"| {cell(d['criterion'])} | {d['result']} | {cell(d['evidence'])} |")
        w("")

    if previous is not None:
        w("## Against the previous round")
        w("")
        if syn.get("previous_priorities"):
            w("| Previous priority | Status | Evidence |")
            w("|---|---|---|")
            for p in syn["previous_priorities"]:
                w(f"| {cell(p['title'])} | {p['status']} | {cell(p['evidence'])} |")
            w("")
        prev_by_key = {r["key"]: r for r in previous.get("reviews", [])}
        w(f"Previous round: {previous.get('date', '?')}"
          f"{' at ' + previous['pin'] if previous.get('pin') else ''}. "
          "Blocker / major / minor per reader, previous then now:")
        w("")
        w("| Reader | Previous | Now | Teach-back, previous then now |")
        w("|---|---|---|---|")
        for r in reviews:
            p = prev_by_key.get(r["key"])
            before = tally(p.get("findings", [])) if p else "not in previous round"
            tb_now = (r.get("teach_back_check") or {}).get("verdict", "n/a")
            tb_before = ((p or {}).get("teach_back_check") or {}).get("verdict", "n/a")
            w(f"| {cell(labels[r['key']])} | {before} | {tally(r.get('findings', []))} | {tb_before} → {tb_now} |")
        w("")
        surviving = []
        total_prev = 0
        for p in previous.get("reviews", []):
            for f in p.get("findings", []):
                total_prev += 1
                if quote_found(f.get("quote", ""), corpus):
                    surviving.append((p["key"], f))
        w(f"Of the previous round's {total_prev} kept findings, {len(surviving)} quote a passage that still "
          "appears in the document. That counts surviving text, not surviving problems: a passage can stay "
          "and its problem be fixed around it.")
        blockers = [(k, f) for k, f in surviving if f.get("severity") == "blocker"]
        if blockers:
            w("")
            w("Previous blockers whose passage survives:")
            w("")
            for k, f in blockers:
                w(f"- {labels.get(k, k)}: {f.get('location')}: \"{f.get('quote')}\"")
        w("")

    personas = sorted([r for r in reviews if r.get("kind") == "persona"],
                      key=lambda r: TIER_ORDER.get(r.get("tier"), 4))
    if personas:
        w("## The readers")
        w("")
        w("Teach-back is the verifier's judgement of what the reader came away with. Goal reached, path "
          "and stop point are the simulated reader's own account, and words read is computed from that "
          "account: self-reports, not measurements.")
        w("")
        w("| Reader | Tier | Mode | Teach-back (verified) | Goal reached (self-report) | Words read / budget | Path | B / M / m |")
        w("|---|---|---|---|---|---|---|---|")
        for r in personas:
            walk = r.get("walk") or {}
            total, uncounted = path_words(walk.get("path"), texts)
            r["_words"], r["_uncounted"] = total, uncounted
            budget = r.get("budget_words")
            over = ""
            if budget:
                over = " over" if total > budget else " within"
            words_cell = f"{total:,}{'+' if uncounted else ''} / {budget:,}{over}" if budget else f"{total:,}{'+' if uncounted else ''}"
            states = " → ".join(s.get("state", "?") for s in walk.get("path") or [])
            tb = (r.get("teach_back_check") or {}).get("verdict", "n/a")
            w(f"| {cell(labels[r['key']])} | {r.get('tier') or ''} | {r.get('mode') or 'walk'} | {tb} | "
              f"{walk.get('goal_reached', '')} | {words_cell} | {cell(states)} | {tally(r.get('findings', []))} |")
        w("")
        w("A `+` after the word count means some locations on the path could not be counted "
          "(listed per reader below).")
        w("")

    if syn.get("themes"):
        w("## Themes")
        w("")
        for t in sorted(syn["themes"], key=lambda x: SEV_ORDER.get(x.get("severity"), 3)):
            w(f"### [{t['severity']}] {t['theme']}")
            w("")
            w(f"Raised by: {names(t.get('raised_by'), labels)}.")
            w("")
            w(t["summary"])
            w("")
            if t.get("locations"):
                w(f"Where: {'; '.join(t['locations'])}.")
                w("")

    tests = ensemble.get("reader_tests") or []
    if tests:
        outcomes: dict[str, int] = {}
        for t in tests:
            outcomes[t.get("outcome", "untested")] = outcomes.get(t.get("outcome", "untested"), 0) + 1
        w("## Predictions tested on real readers so far")
        w("")
        w(", ".join(f"{n} {k}" for k, n in sorted(outcomes.items())) + ".")
        w("")
        for t in tests:
            w(f"- {t.get('hypothesis')}: **{t.get('outcome')}**{(' (' + t['note'] + ')') if t.get('note') else ''}")
        w("")

    if syn.get("validate_with_readers"):
        w("## Check with real readers")
        w("")
        w("Predictions about reader behaviour that drive a priority. A cheap test: give one or two real "
          "readers of that kind the passage, ask them to mark what helps (+) and what hinders (-) as they "
          "read, then ask why.")
        w("")
        for v in syn["validate_with_readers"]:
            w(f"- **{v['hypothesis']}** ({names(v.get('raised_by'), labels)}). Test: {v['test']}")
        w("")

    w("## Per reviewer")
    w("")
    for r in sorted(reviews, key=lambda r: (r.get("kind") != "persona", TIER_ORDER.get(r.get("tier"), 4))):
        w(f"### {labels[r['key']]}")
        w("")
        if r.get("kind") == "persona":
            w(f"Tier: {r.get('tier')}. Goal: {r.get('goal')} Entry: {r.get('entry')}")
            w("")
        w(f"**Verdict.** {r.get('verdict', '')}")
        w("")
        walk = r.get("walk") or {}
        if walk.get("path"):
            w("**Path.** " + " → ".join(f"{s.get('location')} ({s.get('state')})" for s in walk["path"]))
            w("")
            w(f"Walk ended at {walk.get('stop_point')}. {walk.get('stop_reason')} Goal reached: {walk.get('goal_reached')}.")
            if r.get("_uncounted"):
                w(f"Not counted in words read: {', '.join(r['_uncounted'])}.")
            w("")
        if r.get("came_for"):
            w("| Came for | Met | Where |")
            w("|---|---|---|")
            for c in r["came_for"]:
                w(f"| {cell(c['expectation'])} | {c['met']} | {cell(c['where'])} |")
            w("")
        if r.get("teach_back"):
            w(f"**Teach-back.** {r['teach_back']}")
            w("")
            tbc = r.get("teach_back_check")
            if tbc:
                w(f"Verifier: **{tbc.get('verdict')}**. {tbc.get('reason', '')}")
                if tbc.get("takeaways_missed"):
                    w(f"Intended takeaways missed: {'; '.join(tbc['takeaways_missed'])}.")
                w("")
        if r.get("strengths"):
            w("**What works.**")
            w("")
            for s in r["strengths"]:
                w(f"- {s}")
            w("")
        if r.get("top_priorities"):
            w("**This reviewer's priorities.**")
            w("")
            for i, p in enumerate(r["top_priorities"], 1):
                w(f"{i}. {p}")
            w("")
        if r.get("findings"):
            w("**Findings.**")
            w("")
            for f in sorted(r["findings"], key=lambda x: SEV_ORDER.get(x.get("severity"), 3)):
                raised = f" (reported {f['severity_as_reported']}; raised by the tier rule)" if f.get("severity_as_reported") else ""
                beyond = ", past the stop point" if f.get("beyond_stop") else ""
                by_verifier = " (found by the verifier, not the reviewer)" if f.get("found_by") == "verifier" else ""
                w(f"- **[{f.get('severity')} / {f.get('kind')}]**{raised}{by_verifier} {f.get('location')}{beyond}")
                flag = "" if f.get("_quote_ok") is not False else " **(quote not found by the script; check before acting)**"
                w(f"  - Quote: \"{f.get('quote')}\"{flag}")
                w(f"  - Issue: {f.get('issue')}")
                w(f"  - Needed: {f.get('expected')}")
                v = f.get("verification") or {}
                if v.get("verdict") not in (None, "unchecked", "verifier-found"):
                    line = f"  - Verified: {v['verdict']}. {v.get('reason', '')}"
                    if v.get("adjusted"):
                        line += f" Adjusted: {v['adjusted']}"
                    w(line)
                elif f.get("basis") == "recall":
                    w("  - Rests on the reviewer's recall and was not verified.")
            w("")
        if r.get("cap_skipped"):
            w(f"{r['cap_skipped']} major finding(s) went unverified because of the per-reviewer cap.")
            w("")

    dropped = result.get("dropped") or []
    if dropped:
        w("## Dropped findings")
        w("")
        w("Removed before the synthesis because a verifier refuted them or could not find their quote. "
          "Listed so a wrong refutation can be caught.")
        w("")
        for f in dropped:
            v = f.get("verification") or {}
            why = "quote not found" if v.get("quote_found") is False else v.get("verdict")
            w(f"- {labels.get(f.get('reviewer'), f.get('reviewer'))}, {f.get('location')} ({why}): "
              f"{f.get('issue')} Verifier: {v.get('reason', '')}")
        w("")

    w("## Method and caveats")
    w("")
    runner = method.get("runner", "?")
    blind = method.get("blind")
    w(f"- Runner: {runner}; reviewers {'blind to one another' if blind else 'NOT blind: one context wrote every review, so later reviews saw earlier ones'}. "
      f"Model: {method.get('model', '?')}; verifier model: {method.get('verify_model', method.get('model', '?'))}.")
    raised_n = sum(len([f for f in r.get("findings", []) if f.get("found_by") != "verifier"]) for r in reviews) + len(dropped)
    added_n = sum(len([f for f in r.get("findings", []) if f.get("found_by") == "verifier"]) for r in reviews)
    checked_n = sum(len([f for f in r.get("findings", []) if (f.get("verification") or {}).get("verdict") in ("confirmed", "adjusted")]) for r in reviews) + \
        len([f for f in dropped if (f.get("verification") or {}).get("verdict") == "refuted"])
    w(f"- Verification: a verifier located every quote and tried to refute up to "
      f"{method.get('max_verify_per_reviewer', '?')} major claims per reviewer; the rest are unverified. "
      f"Reviewers raised {raised_n} findings; {checked_n} were put to refutation, and {len(dropped)} were dropped "
      f"(refuted or quote not found). Verifiers added {added_n} the reviewers missed.")
    per = [f"{labels.get(r['key'], r['key'])} {r.get('refuted', 0)} of "
           f"{len([f for f in r.get('findings', []) if f.get('found_by') != 'verifier']) + r.get('refuted', 0)}"
           for r in reviews]
    w(f"- Dropped per reviewer: {'; '.join(per)}. A verifier is the same model as the reviewer and can drop "
      "true findings too; read *Dropped findings*.")
    if texts:
        w(f"- Quote check: {stats['quotes_checked']} quotes searched in {len(texts)} file(s); "
          f"{len(stats['quotes_missing'])} not found"
          + (": " + "; ".join(f"{labels.get(k, k)} at {loc}" for k, loc in stats["quotes_missing"]) if stats["quotes_missing"] else "") + ".")
    else:
        w("- Quote check: not run; no reader files were found under the root.")
    w("- No check here measures what every reviewer missed. The verifiers' own search for missed problems "
      "is the only one, and it is the same model again.")
    w("- Simulated readers predict reader problems; they do not observe them. Human experts asked to predict "
      "what real readers will struggle with catch a minority of it and add problems readers never have, so "
      "treat reader-experience findings as hypotheses and test the ones that matter.")
    w("- The reviewers are one model wearing different briefs. Their agreement is weaker evidence than "
      "agreement between independent people, and their satisfaction is not evidence of quality: models "
      "playing readers are kinder than readers, and favour text written by models.")
    if ensemble.get("drafted_with_ai"):
        w("- The document was drafted with an AI model, so expect these reviewers to under-flag its problems; "
          "weigh the editor lenses and the verified correctness findings over reader satisfaction.")
    for line in method.get("log") or []:
        w(f"- Run log: {line}")
    if prev_texts_note:
        w(f"- {prev_texts_note}")
    w("")

    text = "\n".join(out)
    return re.sub(r"\n{3,}", "\n\n", text).rstrip() + "\n", stats


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("ensemble")
    ap.add_argument("result")
    ap.add_argument("-o", "--output", default=None)
    ap.add_argument("--previous", default=None, help="the previous round's result.json")
    ap.add_argument("--root", default=".", help="directory the ensemble's paths are relative to")
    a = ap.parse_args()

    root = under_cwd(a.root)
    ensemble = load_json(under_cwd(a.ensemble))
    result_path = under_cwd(a.result)
    result = load_json(result_path)
    if result.get("status") == "error" and not result.get("reviews"):
        print(f"error: the run failed at stage {result.get('stage')}: {result.get('problems')}", file=sys.stderr)
        return 1
    patterns = list(ensemble.get("reader_files") or [])
    for p in ensemble.get("personas") or []:
        patterns += p.get("reader_files") or []
    texts = resolve_files(patterns, root)
    previous = load_json(under_cwd(a.previous)) if a.previous else None
    report, stats = build(ensemble, result, texts, previous, None)
    out = under_cwd(a.output) if a.output else result_path.parent / "report.md"
    out.write_text(report, encoding="utf-8")
    print(f"wrote {out}: {stats['quotes_checked']} quotes checked, {len(stats['quotes_missing'])} not found")
    return 0


if __name__ == "__main__":
    sys.exit(main())
