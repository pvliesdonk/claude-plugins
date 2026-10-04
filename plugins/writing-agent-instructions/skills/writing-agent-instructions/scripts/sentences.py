#!/usr/bin/env python3
"""Split a Markdown instruction file into numbered sentences for an inventory.

Prints one line per sentence as ``number<TAB>length<TAB>sentence`` so the
output can be tagged by hand, diffed, and grepped. Deterministic and
standard-library only.

Skipped, because they are not prose the agent weighs sentence by sentence:
YAML frontmatter, fenced code blocks, HTML comments, Jinja tags, table rows
and headings. List items are sentences; a bullet that holds several
sentences yields several lines.

Usage:
    python3 sentences.py FILE [FILE ...]
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

_FRONTMATTER = re.compile(r"\A---\n.*?\n---\n", re.S)
_FENCE = re.compile(r"^(```|~~~).*?^\1[^\n]*$", re.S | re.M)
_COMMENT = re.compile(r"<!--.*?-->", re.S)
_JINJA = re.compile(r"\{%.*?%\}|\{\{.*?\}\}", re.S)
_HEADING = re.compile(r"^\s{0,3}#{1,6}\s.*$", re.M)
_TABLE_ROW = re.compile(r"^\s*\|.*$", re.M)
_BULLET = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+", re.M)
# A sentence ends at . ! or ? followed by whitespace and an opening token.
# `e.g.`, `i.e.`, a version number and a path do not end one.
_SPLIT = re.compile(r"(?<!\be\.g)(?<!\bi\.e)(?<!\d)(?<=[.!?])\s+(?=[A-Z0-9`*\"'(\[])")


def sentences(text: str) -> list[str]:
    """Return the prose sentences of a Markdown document, in order."""
    text = _FRONTMATTER.sub("", text)
    text = _FENCE.sub("\n", text)
    text = _COMMENT.sub(" ", text)
    text = _JINJA.sub(" ", text)
    text = _HEADING.sub("\n", text)
    text = _TABLE_ROW.sub("\n", text)
    out: list[str] = []
    for block in re.split(r"\n\s*\n", text):
        # A list item starts a new sentence even when the previous line has
        # no terminal punctuation.
        for item in re.split(r"\n(?=\s*(?:[-*+]|\d+[.)])\s+)", block):
            flat = " ".join(_BULLET.sub("", item, count=1).split())
            if not flat:
                continue
            out.extend(s.strip() for s in _SPLIT.split(flat) if s.strip())
    return out


def _under_cwd(name: str) -> Path:
    """Resolve ``name`` and require it to lie inside the working directory.

    The caller is usually an agent passing a path it chose itself, so the
    script reads only files under the directory it was started in.
    """
    root = Path.cwd().resolve()
    path = (root / name).resolve()
    if root not in path.parents:
        raise SystemExit(f"error: {name!r} is outside the working directory {root}")
    return path


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__, file=sys.stderr)
        return 2
    n = 0
    for name in argv:
        for s in sentences(_under_cwd(name).read_text(encoding="utf-8")):
            n += 1
            print(f"{n}\t{len(s)}\t{s}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
