#!/usr/bin/env python3
"""Validate an Open Knowledge Format (OKF) v0.2 bundle.

Errors implement the §11 conformance rules. Warnings cover the soft guidance that
consumers must tolerate but producers usually want to know about.

Usage:
    python3 validate_okf.py <bundle-dir> [--strict] [--json]

Exit codes: 0 clean, 1 errors (or warnings under --strict), 2 bad invocation.

Only dependency is PyYAML. If it is missing, install with:
    pip install pyyaml --break-system-packages
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("PyYAML required: pip install pyyaml --break-system-packages")

RESERVED = {"index.md", "log.md"}
VALID_STATUS = {"draft", "stable", "deprecated"}
ACTOR_RE = re.compile(r"^(human:[^\s]+|process:[^\s]+|[^\s/]+/[^\s]+)$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
LOG_HEADING_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
FOOTNOTE_REF_RE = re.compile(r"\[\^([^\]]+)\]")
FOOTNOTE_DEF_RE = re.compile(r"^\[\^([^\]]+)\]:", re.MULTILINE)
FENCE_RE = re.compile(r"^(```|~~~)", re.MULTILINE)


class Report:
    def __init__(self) -> None:
        self.errors: list[dict] = []
        self.warnings: list[dict] = []

    def error(self, path: str, msg: str) -> None:
        self.errors.append({"path": path, "message": msg})

    def warn(self, path: str, msg: str) -> None:
        self.warnings.append({"path": path, "message": msg})


def split_frontmatter(text: str):
    """Return (frontmatter_dict_or_None, body, error_message_or_None)."""
    if not text.startswith("---"):
        return None, text, "no frontmatter block"
    lines = text.splitlines()
    if lines[0].strip() != "---":
        return None, text, "no frontmatter block"
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            raw = "\n".join(lines[1:i])
            body = "\n".join(lines[i + 1 :])
            try:
                data = yaml.safe_load(raw)
            except yaml.YAMLError as exc:
                return None, body, f"unparseable YAML frontmatter: {exc}"
            if data is None:
                data = {}
            if not isinstance(data, dict):
                return None, body, "frontmatter is not a YAML mapping"
            return data, body, None
    return None, text, "frontmatter block is never closed"


def parse_date(value) -> dt.date | None:
    if isinstance(value, dt.date) and not isinstance(value, dt.datetime):
        return value
    if isinstance(value, dt.datetime):
        return value.date()
    if isinstance(value, str) and DATE_RE.match(value):
        try:
            return dt.date.fromisoformat(value)
        except ValueError:
            return None
    return None


def check_actor(report: Report, rel: str, field: str, value) -> None:
    if not isinstance(value, str) or not ACTOR_RE.match(value):
        report.warn(
            rel,
            f"{field}: {value!r} does not match the actor convention "
            "(<producer>/<version>, human:<id>, process:<id>)",
        )


def check_trust_fields(report: Report, rel: str, fm: dict) -> None:
    generated = fm.get("generated")
    if generated is not None:
        if not isinstance(generated, dict):
            report.warn(rel, "generated: expected a mapping with 'by' and 'at'")
        else:
            if "by" not in generated:
                report.warn(rel, "generated: 'by' is required within generated")
            else:
                check_actor(report, rel, "generated.by", generated["by"])
            if "at" not in generated:
                report.warn(rel, "generated: 'at' (ISO 8601 datetime) is recommended")

    verified = fm.get("verified")
    if verified is not None:
        entries = verified if isinstance(verified, list) else [verified]
        for entry in entries:
            if not isinstance(entry, dict):
                report.warn(rel, "verified: each entry must be a {by, at} mapping")
                continue
            if "by" in entry:
                check_actor(report, rel, "verified[].by", entry["by"])
            else:
                report.warn(rel, "verified: entry without 'by'")
            if "at" not in entry:
                report.warn(rel, "verified: entry without 'at'")

    status = fm.get("status")
    if status is not None and status not in VALID_STATUS:
        report.warn(rel, f"status: {status!r} is not draft/stable/deprecated")

    if "timestamp" in fm and "generated" not in fm:
        report.warn(rel, "timestamp is a v0.1 field superseded by generated.at")

    stale_after = fm.get("stale_after")
    if stale_after is not None:
        date = parse_date(stale_after)
        if date is None:
            report.warn(rel, f"stale_after: {stale_after!r} is not a YYYY-MM-DD date")
        elif date <= dt.date.today():
            report.warn(rel, f"stale_after {date.isoformat()} has passed; content is stale")


def check_sources(report: Report, rel: str, fm: dict, body: str) -> None:
    sources = fm.get("sources")
    ids: set[str] = set()
    if sources is not None:
        if not isinstance(sources, list):
            report.warn(rel, "sources: expected a list of entries")
        else:
            for entry in sources:
                if not isinstance(entry, dict):
                    report.warn(rel, "sources: each entry must be a mapping")
                    continue
                if not entry.get("resource"):
                    report.warn(rel, "sources: entry without required 'resource'")
                if "id" in entry:
                    ids.add(str(entry["id"]))
                if "author" in entry:
                    check_actor(report, rel, "sources[].author", entry["author"])
                last_mod = entry.get("last_modified")
                if last_mod is not None and parse_date(last_mod) is None:
                    report.warn(rel, f"sources[].last_modified: {last_mod!r} is not YYYY-MM-DD")
            if any("usage_count" in e for e in sources if isinstance(e, dict)):
                has_window = "usage_window" in fm or any(
                    isinstance(e, dict) and "usage_window" in e for e in sources
                )
                if not has_window:
                    report.warn(rel, "usage_count present without a usage_window to frame it")

    if re.search(r"^#+\s*Citations\s*$", body, re.MULTILINE):
        report.warn(rel, "body '# Citations' list is a v0.1 pattern superseded by sources")

    defined = set(FOOTNOTE_DEF_RE.findall(body))
    referenced = set(FOOTNOTE_REF_RE.findall(body)) - defined
    for label in sorted(defined | referenced):
        if ids and label not in ids:
            report.warn(rel, f"footnote [^{label}] has no matching sources[].id")
        elif not ids:
            report.warn(
                rel,
                f"footnote [^{label}] has no sources[].id to resolve against; "
                "give the source a stable 'id'",
            )


def check_attested_computation(report: Report, rel: str, fm: dict, body: str) -> None:
    if fm.get("type") != "Attested Computation":
        return
    if not fm.get("runtime"):
        report.error(rel, "Attested Computation requires 'runtime'")

    has_fence = bool(
        re.search(r"^#+\s*Computation\s*$", body, re.MULTILINE)
    ) and bool(FENCE_RE.search(body) or re.search(r"^\s{4,}\S", body, re.MULTILINE))
    if not fm.get("computation") and not has_fence:
        report.error(
            rel,
            "Attested Computation needs either a 'computation' path or a "
            "'# Computation' body section containing the computation",
        )
    if fm.get("computation") and re.search(r"^#+\s*Computation\s*$", body, re.MULTILINE):
        report.warn(rel, "both a 'computation' path and a '# Computation' body section are present")

    params = fm.get("parameters")
    if params is not None:
        if not isinstance(params, list):
            report.warn(rel, "parameters: expected a list of {name, type, required}")
        else:
            for p in params:
                if not isinstance(p, dict) or "name" not in p:
                    report.warn(rel, "parameters: each entry needs at least a 'name'")

    for field in ("executor", "attester"):
        block = fm.get(field)
        if block is None:
            report.warn(rel, f"{field} absent; the computation cannot be attested end to end")
        elif not isinstance(block, dict) or not block.get("resource"):
            report.warn(rel, f"{field}: expected a mapping with a 'resource'")
    executor = fm.get("executor")
    if isinstance(executor, dict) and not executor.get("receipt"):
        report.warn(rel, "executor.receipt absent; the attester has no declared evidence to inspect")


def check_links(
    report: Report, rel: str, body: str, root: Path, current: Path, prefer_absolute: bool = True
) -> None:
    for target in LINK_RE.findall(body):
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        clean = target.split("#", 1)[0]
        if not clean:
            continue
        if clean.startswith("/"):
            resolved = root / clean.lstrip("/")
        else:
            resolved = (current.parent / clean).resolve()
        if not resolved.exists():
            report.warn(rel, f"link target does not exist: {target}")
        elif prefer_absolute and not clean.startswith("/") and clean.endswith(".md"):
            report.warn(
                rel,
                f"relative link {target}: bundle-relative (/path.md) is recommended, "
                "it survives the file being moved",
            )


def check_concept(report: Report, root: Path, path: Path) -> None:
    rel = str(path.relative_to(root))
    text = path.read_text(encoding="utf-8", errors="replace")
    fm, body, err = split_frontmatter(text)
    if err:
        report.error(rel, err)
        return
    assert fm is not None

    type_value = fm.get("type")
    if not isinstance(type_value, str) or not type_value.strip():
        report.error(rel, "frontmatter must contain a non-empty 'type'")
    if not fm.get("description"):
        report.warn(rel, "no 'description'; index generators and search snippets rely on it")
    if not fm.get("title"):
        report.warn(rel, "no 'title'; consumers will fall back to the filename")

    check_trust_fields(report, rel, fm)
    check_sources(report, rel, fm, body)
    check_attested_computation(report, rel, fm, body)
    check_links(report, rel, body, root, path)


def check_index(report: Report, root: Path, path: Path) -> None:
    rel = str(path.relative_to(root))
    text = path.read_text(encoding="utf-8", errors="replace")
    is_root = path.parent.resolve() == root.resolve()
    fm, body, err = split_frontmatter(text)
    if fm is not None:
        if not is_root:
            report.error(rel, "index.md carries frontmatter; only a bundle-root index.md may")
        else:
            extra = set(fm) - {"okf_version"}
            if extra:
                report.error(
                    rel,
                    f"root index.md frontmatter may only carry okf_version, found: {sorted(extra)}",
                )
            version = str(fm.get("okf_version", ""))
            if version and not re.match(r"^\d+\.\d+$", version):
                report.warn(rel, f"okf_version {version!r} is not <major>.<minor>")
    elif err and err != "no frontmatter block":
        report.error(rel, err)
    elif is_root:
        report.warn(rel, "root index.md does not declare okf_version")

    if not LINK_RE.search(body if fm is not None else text):
        report.warn(rel, "index.md lists no entries")
    check_links(
        report, rel, body if fm is not None else text, root, path, prefer_absolute=False
    )


def check_log(report: Report, root: Path, path: Path) -> None:
    rel = str(path.relative_to(root))
    text = path.read_text(encoding="utf-8", errors="replace")
    headings = LOG_HEADING_RE.findall(text)
    if not headings:
        report.warn(rel, "log.md has no '## YYYY-MM-DD' date headings")
    dates = []
    for heading in headings:
        if not DATE_RE.match(heading):
            report.error(rel, f"log.md date heading is not ISO 8601 YYYY-MM-DD: '## {heading}'")
        else:
            dates.append(heading)
    if dates != sorted(dates, reverse=True):
        report.warn(rel, "log.md entries are not newest first")


def validate(root: Path) -> Report:
    report = Report()
    md_files = sorted(p for p in root.rglob("*.md") if p.is_file())
    if not md_files:
        report.error(str(root), "no markdown files found; this is not an OKF bundle")
        return report

    for path in md_files:
        name = path.name
        if name == "index.md":
            check_index(report, root, path)
        elif name == "log.md":
            check_log(report, root, path)
        else:
            check_concept(report, root, path)

    if not (root / "index.md").exists():
        report.warn(".", "no root index.md; progressive disclosure will be synthesised by consumers")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an OKF v0.2 bundle.")
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--strict", action="store_true", help="treat warnings as failures")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args()

    root = args.bundle
    if not root.is_dir():
        print(f"not a directory: {root}", file=sys.stderr)
        return 2

    report = validate(root)
    failed = bool(report.errors) or (args.strict and bool(report.warnings))

    if args.json:
        print(
            json.dumps(
                {
                    "bundle": str(root),
                    "conformant": not report.errors,
                    "errors": report.errors,
                    "warnings": report.warnings,
                },
                indent=2,
            )
        )
        return 1 if failed else 0

    for item in report.errors:
        print(f"ERROR  {item['path']}: {item['message']}")
    for item in report.warnings:
        print(f"WARN   {item['path']}: {item['message']}")
    verdict = "conformant" if not report.errors else "NOT conformant"
    print(
        f"\n{root}: {verdict} with OKF v0.2 "
        f"({len(report.errors)} errors, {len(report.warnings)} warnings)"
    )
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
