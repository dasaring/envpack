"""Prune old or redundant snapshots based on age, count, or tag absence."""

import os
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import List, Optional


def _snapshot_mtime(path: str) -> datetime:
    """Return the last-modified time of a snapshot file as a UTC datetime."""
    ts = os.path.getmtime(path)
    return datetime.fromtimestamp(ts, tz=timezone.utc)


def find_old_snapshots(directory: str, older_than_days: int) -> List[str]:
    """Return paths of .json snapshot files older than *older_than_days* days."""
    cutoff = datetime.now(tz=timezone.utc) - timedelta(days=older_than_days)
    results = []
    for entry in Path(directory).glob("*.json"):
        if _snapshot_mtime(str(entry)) < cutoff:
            results.append(str(entry))
    return sorted(results)


def find_excess_snapshots(directory: str, keep: int) -> List[str]:
    """Return paths of snapshots beyond the *keep* most-recent files.

    Files are sorted newest-first; anything after index *keep* is returned.
    """
    if keep < 1:
        raise ValueError("keep must be >= 1")
    entries = sorted(
        Path(directory).glob("*.json"),
        key=lambda p: _snapshot_mtime(str(p)),
        reverse=True,
    )
    return [str(p) for p in entries[keep:]]


def prune_snapshots(
    paths: List[str],
    dry_run: bool = False,
    pinned: Optional[List[str]] = None,
) -> List[str]:
    """Delete snapshot files in *paths*, skipping any that are pinned.

    Returns the list of paths that were actually removed (or would be removed
    when *dry_run* is True).
    """
    protected = set(pinned or [])
    removed = []
    for path in paths:
        if path in protected:
            continue
        if not dry_run:
            try:
                os.remove(path)
            except FileNotFoundError:
                pass
        removed.append(path)
    return removed


def prune_summary(removed: List[str], dry_run: bool = False) -> str:
    """Return a human-readable summary of a prune operation."""
    action = "Would remove" if dry_run else "Removed"
    if not removed:
        return "Nothing to prune."
    lines = [f"{action} {len(removed)} snapshot(s):"]
    for path in removed:
        lines.append(f"  {path}")
    return "\n".join(lines)
