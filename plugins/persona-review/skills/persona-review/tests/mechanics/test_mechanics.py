#!/usr/bin/env python3
"""Drive the workflow through run_offline.mjs with canned answers, then render.

No model is called. Each pass releases the answers for one more stage, which
is how a real fallback run proceeds, and checks what the workflow did with
them: the tier rule, the code-level drops, the synthesis gate, the report's
quote flag and word counts.

Run from anywhere:  python3 tests/mechanics/test_mechanics.py
"""

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent.parent / "scripts"
STAGES = [
    [],
    ["review-newcomer", "review-evaluator", "review-style"],
    ["verify-newcomer", "verify-evaluator", "verify-style"],
    ["synthesis"],
]
failures = []


def check(cond, msg):
    print(("ok   " if cond else "FAIL ") + msg)
    if not cond:
        failures.append(msg)


def run_pass(run_dir):
    return subprocess.run(
        ["node", str(SCRIPTS / "run_offline.mjs"), str(HERE / "ensemble.json"), str(run_dir)],
        capture_output=True, text=True, cwd=HERE,
    )


with tempfile.TemporaryDirectory() as tmp:
    # The renderer reads only under its working directory, so the fixtures
    # are copied in and every render runs from the temporary directory.
    for name in ("doc.md", "ensemble.json"):
        shutil.copy(HERE / name, Path(tmp) / name)
    run_dir = Path(tmp) / "run"
    released = []
    expected_pending = [3, 3, 1, None]
    for n, stage in enumerate(STAGES):
        released += stage
        (run_dir / "answers").mkdir(parents=True, exist_ok=True)
        for name in released:
            shutil.copy(HERE / "answers" / f"{name}.json", run_dir / "answers" / f"{name}.json")
        proc = run_pass(run_dir)
        pending = sorted(p.name for p in (run_dir / "pending").glob("*.prompt.md"))
        if expected_pending[n] is None:
            check(proc.returncode == 0, f"pass {n + 1}: result written (exit {proc.returncode}) {proc.stderr[-300:] if proc.returncode else ''}")
        else:
            check(proc.returncode == 3, f"pass {n + 1}: exits 3 with prompts pending (exit {proc.returncode})")
            check(len(pending) == expected_pending[n], f"pass {n + 1}: {expected_pending[n]} prompt(s) pending, got {pending}")
        if n == 2:
            check(not any(p.startswith("synthesis") for p in pending) or len(pending) == 1,
                  "synthesis is only prompted once everything before it is answered")

    result = json.loads((run_dir / "result.json").read_text())
    reviews = {r["key"]: r for r in result["reviews"]}
    newcomer = reviews["newcomer"]["findings"]
    check(len([f for f in newcomer if f.get("found_by") != "verifier"]) == 1, "newcomer: refuted and quote-not-found findings are dropped in code")
    check(newcomer[0]["severity"] == "blocker" and newcomer[0].get("severity_as_reported") == "major",
          "tier rule raises an absent finding that blocks the goal to blocker")
    check(len(result["dropped"]) == 2, "two findings listed as dropped")
    check(reviews["newcomer"]["teach_back_check"]["verdict"] == "wrong", "teach-back verdict carried through")
    check(result["method"]["runner"] == "agent-tool" and result["method"]["blind"] is True, "method records the runner")
    evaluator = reviews["evaluator"]["findings"]
    check(reviews["evaluator"]["mode"] == "read", "a persona without a goal reads rather than walks")
    check(any(f["kind"] == "absent" and f["severity"] == "major" and not f.get("severity_as_reported") for f in evaluator),
          "the tier rule does not apply to a read-mode persona")
    check(reviews["evaluator"]["teach_back_check"]["verdict"] == "n/a", "no teach-back is judged when none was asked for")
    added = [f for f in reviews["newcomer"]["findings"] if f.get("found_by") == "verifier"]
    check(len(added) == 1, "a finding the verifier says the reviewer missed is kept and marked")

    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / "render_report.py"), "ensemble.json",
         "run/result.json", "-o", "run/report.md", "--root", "."],
        capture_output=True, text=True, cwd=tmp,
    )
    check(proc.returncode == 0, f"renderer exits 0 ({proc.stderr.strip()[-300:]})")
    report = (run_dir / "report.md").read_text()
    check("quote not found by the script" in report, "renderer flags the quote the verifier wrongly accepted")
    check("1 not found" in report, "method section counts the missing quote")
    check("| Newcomer with a laptop | primary | walk | wrong | partly |" in report, "readers table row for the newcomer")
    check("found by the verifier, not the reviewer" in report, "verifier-found finding is labelled")
    check("Predictions tested on real readers so far" in report and "1 confirmed" in report, "real-reader test tally rendered")
    check("Verifiers added 1 the reviewers missed" in report, "method counts verifier-added findings")
    check("over |" in report, "newcomer's two sections exceed the 30-word budget")
    check("Settled by: Watch one newcomer" in report, "conflict carries what would settle it")
    check("Done when, measured" in report, "done-when table rendered")

    # A second round against the first: quote survival and the comparison table.
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / "render_report.py"), "ensemble.json",
         "run/result.json", "-o", "run/report2.md", "--root", ".",
         "--previous", "run/result.json"],
        capture_output=True, text=True, cwd=tmp,
    )
    report2 = (run_dir / "report2.md").read_text()
    check("Against the previous round" in report2, "previous-round section rendered")
    check("Previous blockers whose passage survives" in report2, "surviving blocker passage listed")

    # A path outside the working directory is refused.
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / "render_report.py"), "ensemble.json", "run/result.json",
         "-o", "../escaped.md"],
        capture_output=True, text=True, cwd=tmp,
    )
    check(proc.returncode != 0 and "outside the working directory" in proc.stderr + proc.stdout,
          "renderer refuses an output path outside the working directory")

    # A malformed ensemble is rejected before any prompt is written.
    bad = json.loads((HERE / "ensemble.json").read_text())
    bad["lenses"][0]["key"] = "newcomer"
    (Path(tmp) / "bad.json").write_text(json.dumps(bad))
    proc = subprocess.run(["node", str(SCRIPTS / "run_offline.mjs"), str(Path(tmp) / "bad.json"), str(Path(tmp) / "bad")],
                          capture_output=True, text=True)
    check(proc.returncode == 1 and "used twice" in (proc.stderr + proc.stdout), "duplicate keys are rejected")

print(f"\n{'all passed' if not failures else f'{len(failures)} failed'}")
sys.exit(1 if failures else 0)
