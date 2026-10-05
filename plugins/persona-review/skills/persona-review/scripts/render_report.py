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


def heading_of(line: str) -> tuple[int, str] | None:
    """(level, title) for an ATX markdown heading line, else None."""
    level = len(line) - len(line.lstrip("#"))
    if not 1 <= level <= 6 or line[level:level + 1] not in (" ", "\t"):
        return None
    return level, line[level:].strip().rstrip("#").strip()


def section(text: str, heading: str) -> str | None:
    """The text under a markdown heading, up to the next heading of the same or higher level."""
    want = normalise(heading)
    lines = text.splitlines()
    for i, line in enumerate(lines):
        parsed = heading_of(line)
        if parsed and normalise(parsed[1]) == want:
            level = parsed[0]
            out = []
            for nxt in lines[i + 1:]:
                n = heading_of(nxt)
                if n and n[0] <= level:
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

TABLE3 = "|---|---|---|"
RULE_CAVEATS = [
    "- No check here measures what every reviewer missed. The verifiers' own search for missed problems "
    "is the only one, and it is the same model again.",
    "- Simulated readers predict reader problems; they do not observe them. Human experts asked to predict "
    "what real readers will struggle with catch a minority of it and add problems readers never have, so "
    "treat reader-experience findings as hypotheses and test the ones that matter.",
    "- The reviewers are one model wearing different briefs. Their agreement is weaker evidence than "
    "agreement between independent people, and their satisfaction is not evidence of quality: models "
    "playing readers are kinder than readers, and favour text written by models.",
]


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


def plural(n: int, one: str, many: str) -> str:
    return one if n == 1 else many


def verdict_of(check) -> str:
    return (check or {}).get("verdict", "n/a")


class Ctx:
    """Everything the section renderers share."""

    def __init__(self, ensemble, result, texts, previous):
        self.ensemble = ensemble
        self.result = result
        self.syn = result.get("synthesis") or {}
        self.reviews = result.get("reviews", [])
        self.method = result.get("method", {})
        self.dropped = result.get("dropped") or []
        self.labels = label_map(result)
        self.texts = texts
        self.corpus = normalise("\n".join(texts.values()))
        self.previous = previous
        self.stats = {"quotes_checked": 0, "quotes_missing": []}

    def check_quotes(self):
        for r in self.reviews:
            for f in r.get("findings", []):
                self.stats["quotes_checked"] += 1
                f["_quote_ok"] = quote_found(f.get("quote", ""), self.corpus) if self.texts else None
                if f["_quote_ok"] is False:
                    self.stats["quotes_missing"].append((r["key"], f.get("location", "")))

    def count_words(self):
        for r in self.reviews:
            if r.get("kind") == "persona":
                r["_words"], r["_uncounted"] = path_words((r.get("walk") or {}).get("path"), self.texts)


def sec_header(c: Ctx) -> list[str]:
    pin = c.result.get("pin") or c.ensemble.get("pin")
    n_readers = len([r for r in c.reviews if r.get("kind") == "persona"])
    n_lenses = len([r for r in c.reviews if r.get("kind") == "lens"])
    at = f" at {pin}" if pin else ""
    out = [
        f"# Persona review: {c.result.get('title') or c.ensemble.get('title')}",
        "",
        f"Reviewed {c.result.get('date', '')}{at}. "
        f"{n_readers} simulated {plural(n_readers, 'reader', 'readers')} and "
        f"{n_lenses} editor {plural(n_lenses, 'lens', 'lenses')}. "
        "The readers are a model playing people, so every finding about how a reader reacts is a "
        "prediction to test, not an observation; see *Method and caveats*.",
        "",
    ]
    if c.result.get("status") != "ok":
        out += [f"**Run status: {c.result.get('status')}.** No review came back from: "
                f"{names(c.method.get('failed'), c.labels) or 'none'}.", ""]
    return out + ["## Summary", "", c.syn.get("summary", "(no synthesis)"), ""]


def sec_priorities(c: Ctx) -> list[str]:
    if not c.syn.get("priorities"):
        return []
    out = ["## Priorities", ""]
    for i, p in enumerate(c.syn["priorities"], 1):
        out += [f"### {i}. {p['title']}", "", p["rationale"], "",
                f"Raised by: {names(p.get('raised_by'), c.labels)}. Where: {'; '.join(p.get('locations') or [])}.", ""]
    return out


def sec_conflicts(c: Ctx) -> list[str]:
    if not c.syn.get("conflicts"):
        return []
    out = ["## Decisions for the author", "",
           "Readers who want opposite things, or reader friction that collides with a design decision. "
           "The reviews cannot settle these.", ""]
    for i, x in enumerate(c.syn["conflicts"], 1):
        kind = "Readers disagree" if x.get("kind") == "readers-disagree" else "Design collision"
        out += [f"{i}. **{kind}.** {x['description']}", f"   - Between: {names(x.get('between'), c.labels)}."]
        out += [f"   - Option: {o}" for o in x.get("options") or []]
        if x.get("settle_by"):
            out.append(f"   - Settled by: {x['settle_by']}")
        out.append("")
    return out


def sec_done_when(c: Ctx) -> list[str]:
    if not c.syn.get("done_when"):
        return []
    out = ["## Done when, measured", "", "| Criterion | Result | Evidence |", TABLE3]
    out += [f"| {cell(d['criterion'])} | {d['result']} | {cell(d['evidence'])} |" for d in c.syn["done_when"]]
    return out + [""]


def sec_previous(c: Ctx) -> list[str]:
    prev = c.previous
    if prev is None:
        return []
    out = ["## Against the previous round", ""]
    if c.syn.get("previous_priorities"):
        out += ["| Previous priority | Status | Evidence |", TABLE3]
        out += [f"| {cell(p['title'])} | {p['status']} | {cell(p['evidence'])} |" for p in c.syn["previous_priorities"]]
        out.append("")
    prev_by_key = {r["key"]: r for r in prev.get("reviews", [])}
    prev_pin = f" at {prev['pin']}" if prev.get("pin") else ""
    out += [f"Previous round: {prev.get('date', '?')}{prev_pin}. "
            "Blocker / major / minor per reader, previous then now:", "",
            "| Reader | Previous | Now | Teach-back, previous then now |", "|---|---|---|---|"]
    for r in c.reviews:
        p = prev_by_key.get(r["key"])
        before = tally(p.get("findings", [])) if p else "not in previous round"
        tb_before = verdict_of((p or {}).get("teach_back_check"))
        out.append(f"| {cell(c.labels[r['key']])} | {before} | {tally(r.get('findings', []))} | "
                   f"{tb_before} → {verdict_of(r.get('teach_back_check'))} |")
    out.append("")
    old = [(p["key"], f) for p in prev.get("reviews", []) for f in p.get("findings", [])]
    surviving = [(k, f) for k, f in old if quote_found(f.get("quote", ""), c.corpus)]
    out.append(f"Of the previous round's {len(old)} kept findings, {len(surviving)} quote a passage that still "
               "appears in the document. That counts surviving text, not surviving problems: a passage can stay "
               "and its problem be fixed around it.")
    blockers = [(k, f) for k, f in surviving if f.get("severity") == "blocker"]
    if blockers:
        out += ["", "Previous blockers whose passage survives:", ""]
        out += [f"- {c.labels.get(k, k)}: {f.get('location')}: \"{f.get('quote')}\"" for k, f in blockers]
    return out + [""]


def words_cell(r: dict) -> str:
    total, budget = r["_words"], r.get("budget_words")
    read = f"{total:,}{'+' if r['_uncounted'] else ''}"
    if not budget:
        return read
    verdict = "over" if total > budget else "within"
    return f"{read} / {budget:,} {verdict}"


def sec_readers(c: Ctx) -> list[str]:
    personas = sorted([r for r in c.reviews if r.get("kind") == "persona"],
                      key=lambda r: TIER_ORDER.get(r.get("tier"), 4))
    if not personas:
        return []
    out = ["## The readers", "",
           "Teach-back is the verifier's judgement of what the reader came away with. Goal reached, path "
           "and stop point are the simulated reader's own account, and words read is computed from that "
           "account: self-reports, not measurements.", "",
           "| Reader | Tier | Mode | Teach-back (verified) | Goal reached (self-report) | Words read / budget | Path | B / M / m |",
           "|---|---|---|---|---|---|---|---|"]
    for r in personas:
        walk = r.get("walk") or {}
        states = " → ".join(s.get("state", "?") for s in walk.get("path") or [])
        out.append(f"| {cell(c.labels[r['key']])} | {r.get('tier') or ''} | {r.get('mode') or 'walk'} | "
                   f"{verdict_of(r.get('teach_back_check'))} | {walk.get('goal_reached', '')} | {words_cell(r)} | "
                   f"{cell(states)} | {tally(r.get('findings', []))} |")
    return out + ["", "A `+` after the word count means some locations on the path could not be counted "
                  "(listed per reader below).", ""]


def sec_themes(c: Ctx) -> list[str]:
    if not c.syn.get("themes"):
        return []
    out = ["## Themes", ""]
    for t in sorted(c.syn["themes"], key=lambda x: SEV_ORDER.get(x.get("severity"), 3)):
        out += [f"### [{t['severity']}] {t['theme']}", "", f"Raised by: {names(t.get('raised_by'), c.labels)}.", "",
                t["summary"], ""]
        if t.get("locations"):
            out += [f"Where: {'; '.join(t['locations'])}.", ""]
    return out


def sec_reader_tests(c: Ctx) -> list[str]:
    tests = c.ensemble.get("reader_tests") or []
    if not tests:
        return []
    outcomes: dict[str, int] = {}
    for t in tests:
        outcomes[t.get("outcome", "untested")] = outcomes.get(t.get("outcome", "untested"), 0) + 1
    out = ["## Predictions tested on real readers so far", "",
           ", ".join(f"{n} {k}" for k, n in sorted(outcomes.items())) + ".", ""]
    for t in tests:
        note = f" ({t['note']})" if t.get("note") else ""
        out.append(f"- {t.get('hypothesis')}: **{t.get('outcome')}**{note}")
    return out + [""]


def sec_validate(c: Ctx) -> list[str]:
    if not c.syn.get("validate_with_readers"):
        return []
    out = ["## Check with real readers", "",
           "Predictions about reader behaviour that drive a priority. A cheap test: give one or two real "
           "readers of that kind the passage, ask them to mark what helps (+) and what hinders (-) as they "
           "read, then ask why.", ""]
    out += [f"- **{v['hypothesis']}** ({names(v.get('raised_by'), c.labels)}). Test: {v['test']}"
            for v in c.syn["validate_with_readers"]]
    return out + [""]


def finding_lines(f: dict) -> list[str]:
    raised = f" (reported {f['severity_as_reported']}; raised by the tier rule)" if f.get("severity_as_reported") else ""
    beyond = ", past the stop point" if f.get("beyond_stop") else ""
    by_verifier = " (found by the verifier, not the reviewer)" if f.get("found_by") == "verifier" else ""
    flag = "" if f.get("_quote_ok") is not False else " **(quote not found by the script; check before acting)**"
    out = [f"- **[{f.get('severity')} / {f.get('kind')}]**{raised}{by_verifier} {f.get('location')}{beyond}",
           f"  - Quote: \"{f.get('quote')}\"{flag}",
           f"  - Issue: {f.get('issue')}",
           f"  - Needed: {f.get('expected')}"]
    v = f.get("verification") or {}
    if v.get("verdict") not in (None, "unchecked", "verifier-found"):
        line = f"  - Verified: {v['verdict']}. {v.get('reason', '')}"
        if v.get("adjusted"):
            line += f" Adjusted: {v['adjusted']}"
        out.append(line)
    elif f.get("basis") == "recall":
        out.append("  - Rests on the reviewer's recall and was not verified.")
    return out


def walk_lines(r: dict) -> list[str]:
    walk = r.get("walk") or {}
    if not walk.get("path"):
        return []
    out = ["**Path.** " + " → ".join(f"{s.get('location')} ({s.get('state')})" for s in walk["path"]), "",
           f"Walk ended at {walk.get('stop_point')}. {walk.get('stop_reason')} Goal reached: {walk.get('goal_reached')}."]
    if r.get("_uncounted"):
        out.append(f"Not counted in words read: {', '.join(r['_uncounted'])}.")
    return out + [""]


def teach_back_lines(r: dict) -> list[str]:
    if not r.get("teach_back"):
        return []
    out = [f"**Teach-back.** {r['teach_back']}", ""]
    tbc = r.get("teach_back_check")
    if tbc:
        out.append(f"Verifier: **{tbc.get('verdict')}**. {tbc.get('reason', '')}")
        if tbc.get("takeaways_missed"):
            out.append(f"Intended takeaways missed: {'; '.join(tbc['takeaways_missed'])}.")
        out.append("")
    return out


def reviewer_lines(c: Ctx, r: dict) -> list[str]:
    out = [f"### {c.labels[r['key']]}", ""]
    if r.get("kind") == "persona":
        out += [f"Tier: {r.get('tier')}. Goal: {r.get('goal')} Entry: {r.get('entry')}", ""]
    out += [f"**Verdict.** {r.get('verdict', '')}", ""]
    out += walk_lines(r)
    if r.get("came_for"):
        out += ["| Came for | Met | Where |", TABLE3]
        out += [f"| {cell(x['expectation'])} | {x['met']} | {cell(x['where'])} |" for x in r["came_for"]]
        out.append("")
    out += teach_back_lines(r)
    if r.get("strengths"):
        out += ["**What works.**", ""] + [f"- {s}" for s in r["strengths"]] + [""]
    if r.get("top_priorities"):
        out += ["**This reviewer's priorities.**", ""]
        out += [f"{i}. {p}" for i, p in enumerate(r["top_priorities"], 1)] + [""]
    if r.get("findings"):
        out += ["**Findings.**", ""]
        for f in sorted(r["findings"], key=lambda x: SEV_ORDER.get(x.get("severity"), 3)):
            out += finding_lines(f)
        out.append("")
    if r.get("cap_skipped"):
        out += [f"{r['cap_skipped']} major finding(s) went unverified because of the per-reviewer cap.", ""]
    return out


def sec_reviewers(c: Ctx) -> list[str]:
    out = ["## Per reviewer", ""]
    for r in sorted(c.reviews, key=lambda r: (r.get("kind") != "persona", TIER_ORDER.get(r.get("tier"), 4))):
        out += reviewer_lines(c, r)
    return out


def sec_dropped(c: Ctx) -> list[str]:
    if not c.dropped:
        return []
    out = ["## Dropped findings", "",
           "Removed before the synthesis because a verifier refuted them or could not find their quote. "
           "Listed so a wrong refutation can be caught.", ""]
    for f in c.dropped:
        v = f.get("verification") or {}
        why = "quote not found" if v.get("quote_found") is False else v.get("verdict")
        out.append(f"- {c.labels.get(f.get('reviewer'), f.get('reviewer'))}, {f.get('location')} ({why}): "
                   f"{f.get('issue')} Verifier: {v.get('reason', '')}")
    return out + [""]


def own(r: dict) -> list[dict]:
    """The findings a reviewer raised itself, kept after verification."""
    return [f for f in r.get("findings", []) if f.get("found_by") != "verifier"]


def sec_method(c: Ctx) -> list[str]:
    m = c.method
    blind = ("blind to one another" if m.get("blind")
             else "NOT blind: one context wrote every review, so later reviews saw earlier ones")
    raised_n = sum(len(own(r)) for r in c.reviews) + len(c.dropped)
    added_n = sum(len(r.get("findings", [])) - len(own(r)) for r in c.reviews)
    put_to_refutation = ("confirmed", "adjusted")
    checked_n = sum(1 for r in c.reviews for f in r.get("findings", [])
                    if (f.get("verification") or {}).get("verdict") in put_to_refutation)
    checked_n += sum(1 for f in c.dropped if (f.get("verification") or {}).get("verdict") == "refuted")
    per = [f"{c.labels.get(r['key'], r['key'])} {r.get('refuted', 0)} of {len(own(r)) + r.get('refuted', 0)}"
           for r in c.reviews]
    out = ["## Method and caveats", "",
           f"- Runner: {m.get('runner', '?')}; reviewers {blind}. "
           f"Model: {m.get('model', '?')}; verifier model: {m.get('verify_model', m.get('model', '?'))}.",
           f"- Verification: a verifier located every quote and tried to refute up to "
           f"{m.get('max_verify_per_reviewer', '?')} major claims per reviewer; the rest are unverified. "
           f"Reviewers raised {raised_n} findings; {checked_n} were put to refutation, and {len(c.dropped)} were dropped "
           f"(refuted or quote not found). Verifiers added {added_n} the reviewers missed.",
           f"- Dropped per reviewer: {'; '.join(per)}. A verifier is the same model as the reviewer and can drop "
           "true findings too; read *Dropped findings*."]
    missing = c.stats["quotes_missing"]
    if c.texts:
        where = ": " + "; ".join(f"{c.labels.get(k, k)} at {loc}" for k, loc in missing) if missing else ""
        out.append(f"- Quote check: {c.stats['quotes_checked']} quotes searched in {len(c.texts)} file(s); "
                   f"{len(missing)} not found{where}.")
    else:
        out.append("- Quote check: not run; no reader files were found under the root.")
    out += RULE_CAVEATS
    if c.ensemble.get("drafted_with_ai"):
        out.append("- The document was drafted with an AI model, so expect these reviewers to under-flag its problems; "
                   "weigh the editor lenses and the verified correctness findings over reader satisfaction.")
    out += [f"- Run log: {line}" for line in m.get("log") or []]
    return out + [""]


SECTIONS = [sec_header, sec_priorities, sec_conflicts, sec_done_when, sec_previous, sec_readers,
            sec_themes, sec_reader_tests, sec_validate, sec_reviewers, sec_dropped, sec_method]


def build(ensemble: dict, result: dict, texts: dict[str, str], previous: dict | None) -> tuple[str, dict]:
    c = Ctx(ensemble, result, texts, previous)
    c.check_quotes()
    c.count_words()
    lines: list[str] = []
    for render in SECTIONS:
        lines += render(c)
    text = "\n".join(lines)
    return re.sub(r"\n{3,}", "\n\n", text).rstrip() + "\n", c.stats


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
    report, stats = build(ensemble, result, texts, previous)
    out = under_cwd(a.output) if a.output else result_path.parent / "report.md"
    out.write_text(report, encoding="utf-8")
    print(f"wrote {out}: {stats['quotes_checked']} quotes checked, {len(stats['quotes_missing'])} not found")
    return 0


if __name__ == "__main__":
    sys.exit(main())
