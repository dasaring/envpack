"""Deduplication utilities for snapshots."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Dict, List, NamedTuple


class DedupGroup(NamedTuple):
    digest: str
    paths: List[Path]

    def is_duplicate(self) -> bool:
        return len(self.paths) > 1

    def canonical(self) -> Path:
        """Return the lexicographically first path as the canonical copy."""
        return sorted(self.paths)[0]

    def duplicates(self) -> List[Path]:
        """Return all paths except the canonical one."""
        return [p for p in sorted(self.paths) if p != self.canonical()]


def _digest(snapshot: Dict[str, str]) -> str:
    """Return a stable SHA-256 digest of snapshot contents."""
    canonical = json.dumps(snapshot, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()


def find_duplicates(paths: List[Path]) -> List[DedupGroup]:
    """Group snapshot files that have identical contents.

    Only groups with more than one member are returned.
    """
    buckets: Dict[str, List[Path]] = {}
    for path in paths:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        digest = _digest(data)
        buckets.setdefault(digest, []).append(path)
    return [
        DedupGroup(digest=d, paths=ps)
        for d, ps in buckets.items()
        if len(ps) > 1
    ]


def find_duplicates_in_dir(directory: Path) -> List[DedupGroup]:
    """Scan *directory* for duplicate snapshot JSON files."""
    if not directory.is_dir():
        raise NotADirectoryError(f"{directory} is not a directory")
    paths = sorted(directory.glob("*.json"))
    return find_duplicates(paths)


def dedup_summary(groups: List[DedupGroup]) -> str:
    """Return a human-readable summary of duplicate groups."""
    if not groups:
        return "No duplicates found."
    lines = [f"Found {len(groups)} duplicate group(s):"]
    for g in groups:
        lines.append(f"  [{g.digest[:12]}] canonical: {g.canonical()}")
        for dup in g.duplicates():
            lines.append(f"    duplicate: {dup}")
    return "\n".join(lines)
