"""snapshot_diff_summary.py — produce human-readable diff summaries between two snapshot files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import NamedTuple

from envpack.diff import DiffResult, compute  # compute(a, b) -> DiffResult


class FileDiffSummary(NamedTuple):
    path_a: str
    path_b: str
    added: list[str]
    removed: list[str]
    changed: list[str]
    is_identical: bool

    def to_dict(self) -> dict:
        return {
            "path_a": self.path_a,
            "path_b": self.path_b,
            "added": self.added,
            "removed": self.removed,
            "changed": self.changed,
            "is_identical": self.is_identical,
        }

    def render(self) -> str:
        if self.is_identical:
            return f"[identical] {self.path_a}  ==  {self.path_b}"
        lines = [f"diff  {self.path_a}  vs  {self.path_b}"]
        for k in sorted(self.added):
            lines.append(f"  + {k}")
        for k in sorted(self.removed):
            lines.append(f"  - {k}")
        for k in sorted(self.changed):
            lines.append(f"  ~ {k}")
        return "\n".join(lines)


def _load(path: str | Path) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def diff_files(path_a: str | Path, path_b: str | Path) -> FileDiffSummary:
    """Load two snapshot files and return a FileDiffSummary."""
    a = _load(path_a)
    b = _load(path_b)
    result: DiffResult = compute(a, b)
    return FileDiffSummary(
        path_a=str(path_a),
        path_b=str(path_b),
        added=list(result.added.keys()),
        removed=list(result.removed.keys()),
        changed=list(result.changed.keys()),
        is_identical=result.is_empty(),
    )


def batch_diff(
    pairs: list[tuple[str | Path, str | Path]]
) -> list[FileDiffSummary]:
    """Diff multiple pairs of snapshot files."""
    return [diff_files(a, b) for a, b in pairs]


def render_batch(summaries: list[FileDiffSummary]) -> str:
    """Render a list of FileDiffSummary objects as a single report string."""
    if not summaries:
        return "(no comparisons)"
    return "\n\n".join(s.render() for s in summaries)
