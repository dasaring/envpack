"""chain.py — apply a sequence of snapshots in order, merging each into the next."""
from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from envpack.snapshot import load, save
from envpack.merge import merge_snapshots, MergeConflictError


class ChainError(Exception):
    """Raised when a chain operation cannot be completed."""


def build_chain(snapshot_paths: List[str | Path]) -> dict:
    """Merge a list of snapshot files in order, later entries win.

    Args:
        snapshot_paths: Ordered list of paths to snapshot JSON files.

    Returns:
        A single merged snapshot dict.

    Raises:
        ChainError: If the list is empty or a file cannot be loaded.
        MergeConflictError: Propagated from merge_snapshots when strategy='error'.
    """
    if not snapshot_paths:
        raise ChainError("snapshot_paths must contain at least one entry")

    snapshots: List[dict] = []
    for p in snapshot_paths:
        path = Path(p)
        if not path.exists():
            raise ChainError(f"Snapshot file not found: {path}")
        snapshots.append(load(str(path)))

    return merge_snapshots(snapshots, strategy="last")


def save_chain(
    snapshot_paths: List[str | Path],
    output_path: str | Path,
    *,
    label: Optional[str] = None,
) -> Path:
    """Build a chain and save the result to *output_path*.

    Args:
        snapshot_paths: Ordered list of paths to snapshot JSON files.
        output_path: Destination path for the merged snapshot.
        label: Optional human-readable label stored in the snapshot metadata.

    Returns:
        The resolved output Path.
    """
    merged = build_chain(snapshot_paths)
    if label is not None:
        merged["__chain_label__"] = label
    merged["__chain_sources__"] = [str(Path(p).resolve()) for p in snapshot_paths]
    out = Path(output_path)
    save(merged, str(out))
    return out


def describe_chain(snapshot_paths: List[str | Path]) -> str:
    """Return a human-readable summary of what a chain would produce.

    Lists each file and the number of keys it contributes or overrides.
    """
    if not snapshot_paths:
        return "Empty chain — no snapshots provided."

    lines: List[str] = ["Chain order (first → last wins):"]
    running: dict = {}
    for i, p in enumerate(snapshot_paths, start=1):
        path = Path(p)
        snap = load(str(path)) if path.exists() else {}
        new_keys = [k for k in snap if k not in running]
        overridden = [k for k in snap if k in running and running[k] != snap[k]]
        running.update(snap)
        lines.append(
            f"  [{i}] {path.name}: {len(snap)} keys "
            f"(+{len(new_keys)} new, ~{len(overridden)} overridden)"
        )
    lines.append(f"  => Total keys in merged result: {len(running)}")
    return "\n".join(lines)
