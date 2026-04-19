"""Named snapshot comparison utilities for envpack."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from envpack.snapshot import load
from envpack.diff import diff_snapshots, DiffResult, summary


def compare_files(
    path_a: str | Path,
    path_b: str | Path,
) -> DiffResult:
    """Load two snapshot files and return their diff."""
    snap_a = load(Path(path_a))
    snap_b = load(Path(path_b))
    return diff_snapshots(snap_a, snap_b)


def compare_summary(
    path_a: str | Path,
    path_b: str | Path,
) -> str:
    """Return a human-readable summary string comparing two snapshot files."""
    result = compare_files(path_a, path_b)
    return summary(result)


def compare_to_current(
    path: str | Path,
    keys: Optional[list[str]] = None,
) -> DiffResult:
    """Compare a saved snapshot file against the current environment."""
    import os
    from envpack.snapshot import capture

    saved = load(Path(path))
    current = capture(keys=keys if keys else list(saved.keys()))
    return diff_snapshots(saved, current)


def report(
    result: DiffResult,
    *,
    verbose: bool = False,
) -> str:
    """Format a DiffResult into a detailed report string."""
    lines: list[str] = []
    if result["added"]:
        lines.append("Added:")
        for k, v in sorted(result["added"].items()):
            lines.append(f"  + {k}={v if verbose else '***'}")
    if result["removed"]:
        lines.append("Removed:")
        for k, v in sorted(result["removed"].items()):
            lines.append(f"  - {k}={v if verbose else '***'}")
    if result["changed"]:
        lines.append("Changed:")
        for k, (old, new) in sorted(result["changed"].items()):
            if verbose:
                lines.append(f"  ~ {k}: {old!r} -> {new!r}")
            else:
                lines.append(f"  ~ {k}")
    if not lines:
        lines.append("No differences found.")
    return "\n".join(lines)
