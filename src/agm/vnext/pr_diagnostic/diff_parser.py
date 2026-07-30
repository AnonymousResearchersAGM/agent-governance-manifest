"""Safe, deterministic unified-diff parsing for diagnostic locations."""
from __future__ import annotations

import re
from dataclasses import dataclass

from ..models import VNextError

_HUNK = re.compile(r"^@@ -(?P<old>\d+)(?:,(?P<old_count>\d+))? \+(?P<new>\d+)(?:,(?P<new_count>\d+))? @@")

@dataclass(frozen=True)
class DiffLocation:
    path: str
    added: tuple[str, ...]
    removed: tuple[str, ...]
    hunk: str

def _path(value: str) -> str | None:
    value = value.strip()
    if value == "/dev/null": return None
    if value.startswith(("a/", "b/")): value = value[2:]
    if not value or value.startswith("/") or ".." in value.replace("\\", "/").split("/"):
        raise VNextError("Malformed or unsafe unified diff path")
    return value.replace("\\", "/")

def parse_verified_diff(content: str) -> tuple[DiffLocation, ...]:
    """Parse only unified diff facts; caller context never supplies locations."""
    if not content.startswith("diff --git "):
        raise VNextError("Verified diff must start with a unified diff header")
    locations: list[DiffLocation] = []; current: str | None = None; old_path: str | None = None; hunk = ""; added: list[str] = []; removed: list[str] = []
    old_line = new_line = None
    def flush() -> None:
        nonlocal added, removed, hunk
        if current and (added or removed): locations.append(DiffLocation(current, tuple(added), tuple(removed), hunk))
        added=[]; removed=[]; hunk=""
    for line in content.splitlines():
        if line.startswith("diff --git "):
            flush(); current=old_path=None; old_line=new_line=None
            fields=line.split()
            if len(fields) != 4: raise VNextError("Malformed unified diff header")
            _path(fields[2]); _path(fields[3])
            continue
        if line.startswith("--- "):
            old_path=_path(line[4:])
            continue
        if line.startswith("+++ "):
            current=_path(line[4:]) or old_path; continue
        match=_HUNK.match(line)
        if match:
            flush(); old_line=int(match.group("old")); new_line=int(match.group("new")); hunk=line; continue
        if old_line is None or new_line is None: continue
        if line.startswith("+") and not line.startswith("+++"):
            added.append(str(new_line)); new_line += 1
        elif line.startswith("-") and not line.startswith("---"):
            removed.append(str(old_line)); old_line += 1
        elif line.startswith(" "):
            old_line += 1; new_line += 1
    flush()
    if not locations:
        raise VNextError("Verified diff contains no parseable changed hunks")
    return tuple(locations)

def compact_ranges(lines: tuple[str, ...]) -> tuple[str, ...]:
    numbers = sorted({int(line) for line in lines})
    if not numbers: return ()
    out=[]; start=previous=numbers[0]
    for number in numbers[1:]:
        if number == previous + 1: previous=number; continue
        out.append(str(start) if start == previous else f"{start}–{previous}"); start=previous=number
    out.append(str(start) if start == previous else f"{start}–{previous}")
    return tuple(out)
