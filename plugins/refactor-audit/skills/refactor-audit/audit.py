#!/usr/bin/env python3
"""Read-only refactor-triage audit for a Python source tree.

Runs radon (hard dependency) plus lizard / ruff / vulture / git churn when
available, then ranks files by the hotspot model: churn x cyclomatic
complexity. Emits a Markdown triage report and a machine-readable JSON shaped
to seed a structural-health ratchet baseline.

Modifies nothing. Any analyser other than radon that is absent is skipped with
a note rather than crashing.

Run with the analysers injected so their console scripts are on PATH:

    uv run --with radon --with lizard --with vulture \
        python "${CLAUDE_PLUGIN_ROOT}/skills/refactor-audit/audit.py" SRC
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path


# --- Policy: the hotspot score lives here and nowhere else. ----------------
# Complexity says what is ugly; churn x complexity says what is ugly AND
# changes often, which is where refactoring pays. The `or 1` floor lets
# complexity still rank files when git history is shallow or absent.
def hotspot_score(churn: int, cc_total: int) -> int:
    return (churn or 1) * cc_total


SCHEMA_VERSION = 1

# Policy: a one-time audit optimises for signal completeness, not low
# per-commit noise, so it runs a FIXED broad smell set independent of the
# target project's own (often minimal) ruff config — making results
# reproducible and comparable across projects. PLR0904 (god-class by shape)
# is preview-gated; radon scores a class of many trivial methods as low
# complexity and misses it, so we force it on. ruff has no
# too-many-instance-attributes rule (PLR0902 is pylint-only) — cohesion is
# the better god-class signal there; see SKILL.md.
RUFF_AUDIT_SELECT = "C90,PLR,B,SIM,PERF,RUF,TRY,FBT"


@dataclass
class FileMetrics:
    cc_total: int = 0
    cc_max: int = 0
    cc_blocks: int = 0
    mi: float | None = None
    loc: int | None = None
    sloc: int | None = None
    churn: int = 0
    worst_functions: list[dict] = field(default_factory=list)

    @property
    def cc_avg(self) -> float:
        return round(self.cc_total / self.cc_blocks, 2) if self.cc_blocks else 0.0

    @property
    def hotspot(self) -> int:
        return hotspot_score(self.churn, self.cc_total)


def _run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False)


def _rel(path: str, repo_root: Path) -> str:
    try:
        return os.path.relpath(Path(path).resolve(), repo_root)
    except ValueError:
        return path


# --- radon (hard dependency) ----------------------------------------------
def collect_radon(root: Path, repo_root: Path, files: dict[str, FileMetrics]) -> None:
    cc = _run(["radon", "cc", "-j", "-s", str(root)], repo_root)
    for path, blocks in json.loads(cc.stdout or "{}").items():
        key = _rel(path, repo_root)
        fm = files.setdefault(key, FileMetrics())
        for b in blocks:
            if not isinstance(b, dict) or "complexity" not in b:
                continue
            c = b["complexity"]
            fm.cc_total += c
            fm.cc_blocks += 1
            fm.cc_max = max(fm.cc_max, c)

    mi = _run(["radon", "mi", "-j", str(root)], repo_root)
    for path, data in json.loads(mi.stdout or "{}").items():
        if isinstance(data, dict) and "mi" in data:
            files.setdefault(_rel(path, repo_root), FileMetrics()).mi = round(
                data["mi"], 1
            )

    raw = _run(["radon", "raw", "-j", str(root)], repo_root)
    for path, data in json.loads(raw.stdout or "{}").items():
        if not isinstance(data, dict):
            continue
        fm = files.setdefault(_rel(path, repo_root), FileMetrics())
        fm.loc = data.get("loc")
        fm.sloc = data.get("sloc")


# --- lizard (worst functions, cross-checks radon) -------------------------
def collect_lizard(
    root: Path, repo_root: Path, files: dict[str, FileMetrics], cc_threshold: int
) -> list[dict]:
    import importlib

    lizard = importlib.import_module("lizard")

    worst: list[dict] = []
    for finfo in lizard.analyze([str(root)]):
        key = _rel(finfo.filename, repo_root)
        for fn in finfo.function_list:
            rec = {
                "file": key,
                "name": fn.name,
                "ccn": fn.cyclomatic_complexity,
                "length": fn.length,
                "params": fn.parameter_count,
                "line": fn.start_line,
            }
            if fn.cyclomatic_complexity >= cc_threshold:
                worst.append(rec)
            files.setdefault(key, FileMetrics())
    worst.sort(key=lambda r: r["ccn"], reverse=True)
    for r in worst:
        files[r["file"]].worst_functions.append(r)
    return worst


# --- ruff (repo-wide smell inventory) -------------------------------------
_RUFF_STAT = re.compile(r"^\s*(\d+)\s+([A-Z]+\d+)\s+(.*)$")


def collect_ruff(root: Path, repo_root: Path, select: str) -> list[dict]:
    res = _run(
        [
            "ruff",
            "check",
            str(root),
            "--statistics",
            "--no-cache",
            "--preview",
            "--select",
            select,
            "--extend-select",
            "PLR0904",
        ],
        repo_root,
    )
    smells = []
    for line in res.stdout.splitlines():
        m = _RUFF_STAT.match(line)
        if m:
            smells.append(
                {"count": int(m.group(1)), "code": m.group(2), "message": m.group(3)}
            )
    smells.sort(key=lambda s: s["count"], reverse=True)
    return smells


# --- vulture (dead-code candidates, triage input not truth) ---------------
_VULT = re.compile(r"^(.*?):(\d+): (.*?) \((\d+)% confidence\)$")


def collect_vulture(root: Path, repo_root: Path, min_conf: int) -> list[dict]:
    res = _run(["vulture", str(root), "--min-confidence", str(min_conf)], repo_root)
    dead = []
    for line in res.stdout.splitlines():
        m = _VULT.match(line)
        if m:
            dead.append(
                {
                    "file": _rel(m.group(1), repo_root),
                    "line": int(m.group(2)),
                    "message": m.group(3),
                    "confidence": int(m.group(4)),
                }
            )
    dead.sort(key=lambda d: d["confidence"], reverse=True)
    return dead


# --- git churn (the hotspot multiplier) -----------------------------------
def collect_churn(
    root: Path, repo_root: Path, days: int, files: dict[str, FileMetrics]
) -> bool:
    res = _run(
        [
            "git",
            "log",
            f"--since={days} days ago",
            "--name-only",
            "--pretty=format:",
            "--",
            str(root),
        ],
        repo_root,
    )
    if res.returncode != 0:
        return False
    counts = Counter(
        line.strip() for line in res.stdout.splitlines() if line.strip().endswith(".py")
    )
    for path, n in counts.items():
        files.setdefault(_rel(path, repo_root), FileMetrics()).churn = n
    return True


def discover_repo_root(start: Path) -> Path:
    res = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=start,
        capture_output=True,
        text=True,
        check=False,
    )
    if res.returncode == 0:
        return Path(res.stdout.strip())
    return start


# --- report assembly -------------------------------------------------------
def build_json(args, repo_root, files, smells, dead, available, git_ok) -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "source_root": str(args.source_root),
        "repo_root": str(repo_root),
        "churn_window_days": args.churn_days,
        "cc_threshold": args.cc_threshold,
        "hotspot_formula": "(churn or 1) * cc_total",
        "git_available": git_ok,
        "analysers": available,
        "files": {
            path: {
                "cc_total": fm.cc_total,
                "cc_avg": fm.cc_avg,
                "cc_max": fm.cc_max,
                "cc_blocks": fm.cc_blocks,
                "mi": fm.mi,
                "loc": fm.loc,
                "sloc": fm.sloc,
                "churn": fm.churn,
                "hotspot": fm.hotspot,
                "worst_functions": fm.worst_functions,
            }
            for path, fm in sorted(
                files.items(), key=lambda kv: kv[1].hotspot, reverse=True
            )
        },
        "smells": smells,
        "dead_code": dead,
        "totals": {
            "files": len(files),
            "cc_total": sum(fm.cc_total for fm in files.values()),
            "smell_count": sum(s["count"] for s in smells),
            "dead_code_candidates": len(dead),
        },
    }


def build_markdown(data, files, smells, dead, worst, available, top) -> str:
    L = []
    skipped = [k for k, v in available.items() if not v]
    L.append("# Refactor-Audit Triage Report\n")
    L.append(
        f"Source: `{data['source_root']}` | churn window: "
        f"{data['churn_window_days']}d | hotspot = `{data['hotspot_formula']}`\n"
    )
    if skipped:
        L.append(f"> Skipped (not installed): {', '.join(skipped)}.\n")
    if not data["git_available"]:
        L.append("> No git history — ranking falls back to complexity only.\n")

    L.append("\n## Top refactoring candidates (churn x complexity)\n")
    L.append("| Rank | File | Hotspot | Churn | CC total | Max CC | MI |")
    L.append("|---|---|---:|---:|---:|---:|---:|")
    ranked = sorted(files.items(), key=lambda kv: kv[1].hotspot, reverse=True)
    for i, (path, fm) in enumerate(ranked[:top], 1):
        mi = "-" if fm.mi is None else f"{fm.mi}"
        L.append(
            f"| {i} | `{path}` | {fm.hotspot} | {fm.churn} | "
            f"{fm.cc_total} | {fm.cc_max} | {mi} |"
        )

    if worst:
        L.append("\n## Worst functions (lizard CCN)\n")
        L.append("| Function | File | CCN | Length | Params |")
        L.append("|---|---|---:|---:|---:|")
        for r in worst[:top]:
            L.append(
                f"| `{r['name']}` | `{r['file']}`:{r['line']} | "
                f"{r['ccn']} | {r['length']} | {r['params']} |"
            )

    if smells:
        L.append("\n## Smell inventory (ruff)\n")
        L.append("| Count | Rule | Description |")
        L.append("|---:|---|---|")
        for s in smells[:25]:
            L.append(f"| {s['count']} | {s['code']} | {s['message']} |")

    if dead:
        L.append("\n## Dead-code candidates (vulture)\n")
        L.append(
            "> Triage input, **not truth** — vulture over-reports on importable / "
            "public-API code. Confirm before deleting; maintain a whitelist.\n"
        )
        L.append("| Confidence | Location | Finding |")
        L.append("|---:|---|---|")
        for d in dead[:top]:
            L.append(
                f"| {d['confidence']}% | `{d['file']}`:{d['line']} | {d['message']} |"
            )

    L.append("\n## What this does not catch\n")
    L.append(
        "- **Semantic drift** — names / abstractions no longer matching behaviour. "
        "No metric sees this; it stays a human or agent-review job.\n"
        "- **vulture / cohesion findings need confirmation** — ranked triage input, "
        "not verified dead code.\n"
    )
    return "\n".join(L) + "\n"


def main() -> int:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("source_root", type=Path, help="Python source tree to audit")
    p.add_argument("--churn-days", type=int, default=90, help="git churn window")
    p.add_argument("--top", type=int, default=15, help="rows per report table")
    p.add_argument(
        "--cc-threshold", type=int, default=10, help="min CCN for worst-functions"
    )
    p.add_argument("--vulture-min-confidence", type=int, default=60)
    p.add_argument(
        "--ruff-select", default=RUFF_AUDIT_SELECT, help="audit smell ruleset"
    )
    p.add_argument(
        "--md",
        type=Path,
        default=Path("refactor-audit.md"),
        help="Markdown triage report output path",
    )
    p.add_argument(
        "--json",
        type=Path,
        default=Path("structural-baseline.json"),
        help="machine-readable ratchet-seed output path",
    )
    args = p.parse_args()

    root = args.source_root
    if not root.exists():
        print(f"error: source root not found: {root}", file=sys.stderr)
        return 2
    repo_root = discover_repo_root(root if root.is_dir() else root.parent)

    if not shutil.which("radon"):
        print(
            "error: radon is required and not on PATH. Run with:\n"
            "  uv run --with radon --with lizard --with vulture "
            'python "${CLAUDE_PLUGIN_ROOT}/skills/refactor-audit/audit.py" ...',
            file=sys.stderr,
        )
        return 2

    files: dict[str, FileMetrics] = {}
    available = {"radon": True}

    collect_radon(root, repo_root, files)
    git_ok = collect_churn(root, repo_root, args.churn_days, files)

    worst: list[dict] = []
    try:
        import importlib.util

        if importlib.util.find_spec("lizard"):
            worst = collect_lizard(root, repo_root, files, args.cc_threshold)
            available["lizard"] = True
        else:
            available["lizard"] = False
    except Exception as e:  # noqa: BLE001 - skip-with-note contract
        print(f"warning: lizard skipped: {e}", file=sys.stderr)
        available["lizard"] = False

    available["ruff"] = bool(shutil.which("ruff"))
    smells = (
        collect_ruff(root, repo_root, args.ruff_select) if available["ruff"] else []
    )

    available["vulture"] = bool(shutil.which("vulture"))
    dead = (
        collect_vulture(root, repo_root, args.vulture_min_confidence)
        if available["vulture"]
        else []
    )

    data = build_json(args, repo_root, files, smells, dead, available, git_ok)
    md = build_markdown(data, files, smells, dead, worst, available, args.top)

    args.json.write_text(json.dumps(data, indent=2))
    args.md.write_text(md)
    print(f"wrote {args.md} and {args.json}")
    print(f"analysers: {available}  git_history: {git_ok}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
