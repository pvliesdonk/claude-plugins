#!/usr/bin/env python3
"""Validate this catalog's marketplace manifest.

Sibling projects publish into `.claude-plugin/marketplace.json` by pushing
straight to the default branch — no pull request, so no review stands
between a release workflow and this file.  Two failures have already
reached `main` unnoticed and neither announced itself:

* the manifest sat at the repository root, where Claude Code does not look
  for it, so the catalog was not loadable at all;
* an entry named a `git-subdir` path that did not exist at any tag it
  listed, so the plugin was uninstallable from the day it was added.

Both are shape questions a machine can answer.  This script answers them.

Run it with no arguments for the offline checks (structure, local sources,
duplicate names).  Pass ``--check-remote`` to additionally resolve every
remote entry against the GitHub API; that needs network and honours
``GITHUB_TOKEN`` for rate limits and private repositories.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST = REPO_ROOT / ".claude-plugin" / "marketplace.json"

# Source types Claude Code resolves, with the keys each one needs.  A type
# absent here is not necessarily invalid upstream — it is unvalidated, which
# for a catalog that publishes automatically is the same risk.
REQUIRED_SOURCE_KEYS: dict[str, tuple[str, ...]] = {
    "github": ("repo",),
    "url": ("url",),
    "git-subdir": ("url", "path"),
    "npm": ("package",),
    "archive": ("url",),
    "command": ("command",),
}
# Types pinned to a mutable ref unless one of these is given.
PINNABLE = {"github", "url", "git-subdir"}

GITHUB_API = "https://api.github.com"


def _fail(errors: list[str], message: str) -> None:
    errors.append(message)


def _check_local_source(where: str, source: str, root: Path, errors: list[str]) -> None:
    """A string source is a path relative to the marketplace root."""
    if source.startswith("/") or ".." in Path(source).parts:
        _fail(errors, f"{where}: local source {source!r} escapes the marketplace root")
        return
    target = (root / source).resolve()
    if not target.is_dir():
        _fail(errors, f"{where}: local source {source!r} is not a directory in this repo")
        return
    if not (target / ".claude-plugin" / "plugin.json").is_file():
        _fail(
            errors,
            f"{where}: {source!r} has no .claude-plugin/plugin.json, so it is not a plugin",
        )


def _check_remote_source(where: str, source: dict[str, Any], errors: list[str]) -> None:
    kind = source.get("source")
    if not isinstance(kind, str):
        _fail(errors, f"{where}: object source has no 'source' type")
        return
    required = REQUIRED_SOURCE_KEYS.get(kind)
    if required is None:
        _fail(errors, f"{where}: unrecognised source type {kind!r}")
        return
    for key in required:
        if not source.get(key):
            _fail(errors, f"{where}: {kind} source is missing {key!r}")
    if kind in PINNABLE and not (source.get("ref") or source.get("sha")):
        _fail(
            errors,
            f"{where}: {kind} source names neither 'ref' nor 'sha', so it follows a moving branch",
        )


def _github_repo_from_url(url: str) -> tuple[str, str] | None:
    marker = "github.com/"
    if marker not in url:
        return None
    tail = url.split(marker, 1)[1].removesuffix(".git").strip("/")
    parts = tail.split("/")
    if len(parts) < 2:
        return None
    return parts[0], parts[1]


def _api_path_exists(owner: str, repo: str, path: str, ref: str) -> bool:
    url = f"{GITHUB_API}/repos/{owner}/{repo}/contents/{path}?ref={ref}"
    request = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(request, timeout=30) as response:  # noqa: S310
            return 200 <= response.status < 300
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return False
        raise


def _check_remote_reachable(where: str, source: dict[str, Any], errors: list[str]) -> None:
    """Resolve a remote entry's plugin manifest at the ref it pins."""
    if source.get("source") != "git-subdir":
        return
    url, path = str(source.get("url", "")), str(source.get("path", ""))
    ref = str(source.get("sha") or source.get("ref") or "")
    repo = _github_repo_from_url(url)
    if repo is None:
        print(f"  skipped (not a GitHub URL): {where}")
        return
    owner, name = repo
    manifest_path = f"{path.strip('/')}/.claude-plugin/plugin.json"
    try:
        found = _api_path_exists(owner, name, manifest_path, ref)
    except urllib.error.URLError as exc:
        _fail(errors, f"{where}: could not reach the GitHub API ({exc})")
        return
    if not found:
        _fail(
            errors,
            f"{where}: {owner}/{name} has no {manifest_path} at {ref} — the entry is uninstallable",
        )
    else:
        print(f"  ok: {where} -> {owner}/{name}@{ref}:{manifest_path}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check-remote",
        action="store_true",
        help="also resolve remote entries against the GitHub API (needs network)",
    )
    args = parser.parse_args()

    errors: list[str] = []

    if not MANIFEST.is_file():
        print(
            f"error: {MANIFEST.relative_to(REPO_ROOT)} is missing. Claude Code reads the "
            "marketplace from that path and no other.",
            file=sys.stderr,
        )
        return 1

    try:
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"error: {MANIFEST.name} is not valid JSON: {exc}", file=sys.stderr)
        return 1

    if not data.get("name"):
        _fail(errors, "manifest: no top-level 'name'")
    owner = data.get("owner")
    if not isinstance(owner, dict) or not owner.get("name"):
        _fail(errors, "manifest: 'owner' must be an object with a 'name' (the validator requires it)")
    if not data.get("description"):
        _fail(errors, "manifest: no top-level 'description' (the validator warns without one)")

    plugins = data.get("plugins")
    if not isinstance(plugins, list) or not plugins:
        _fail(errors, "manifest: 'plugins' must be a non-empty array")
        plugins = []

    root = MANIFEST.parent.parent
    plugin_root = str((data.get("metadata") or {}).get("pluginRoot") or "").strip("/")
    seen: set[str] = set()

    for index, entry in enumerate(plugins):
        if not isinstance(entry, dict):
            _fail(errors, f"plugins[{index}]: not an object")
            continue
        name = entry.get("name")
        where = f"plugins[{index}] ({name or 'unnamed'})"
        if not name:
            _fail(errors, f"plugins[{index}]: no 'name'")
        elif name in seen:
            _fail(errors, f"{where}: duplicate plugin name")
        else:
            seen.add(str(name))

        source = entry.get("source")
        if isinstance(source, str):
            local = f"{plugin_root}/{source}" if plugin_root else source
            _check_local_source(where, local, root, errors)
        elif isinstance(source, dict):
            before = len(errors)
            _check_remote_source(where, source, errors)
            # Only resolve an entry whose shape held up: a missing url or
            # ref would otherwise produce a second, derived complaint.
            if args.check_remote and len(errors) == before:
                _check_remote_reachable(where, source, errors)
        else:
            _fail(errors, f"{where}: 'source' must be a string path or an object")

    if errors:
        print(f"{MANIFEST.relative_to(REPO_ROOT)} is not publishable:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    print(f"{MANIFEST.relative_to(REPO_ROOT)}: {len(plugins)} entries, all valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
