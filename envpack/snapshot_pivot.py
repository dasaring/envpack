"""snapshot_pivot.py — transpose a list of snapshot files into a key-centric view.

Given multiple snapshot files, build a mapping of
  key -> {filename: value, ...}
so you can see, for every environment variable, which value each snapshot holds.
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

from envpack.snapshot import load


class PivotError(Exception):
    pass


# PivotTable maps key -> {snapshot_label: value}
PivotTable = Dict[str, Dict[str, Optional[str]]]


def build_pivot(snapshot_paths: List[Path]) -> PivotTable:
    """Return a key-centric view across all supplied snapshot files.

    Missing keys in a particular snapshot are represented as None.
    """
    if not snapshot_paths:
        raise PivotError("At least one snapshot path is required.")

    labels: List[str] = [p.name for p in snapshot_paths]
    snapshots: List[dict] = []
    for p in snapshot_paths:
        if not p.exists():
            raise PivotError(f"Snapshot file not found: {p}")
        snapshots.append(load(str(p)))

    all_keys: List[str] = sorted(
        {k for snap in snapshots for k in snap}
    )

    pivot: PivotTable = {}
    for key in all_keys:
        pivot[key] = {label: snap.get(key) for label, snap in zip(labels, snapshots)}

    return pivot


def pivot_to_rows(pivot: PivotTable) -> List[dict]:
    """Convert a PivotTable to a list of row dicts suitable for display or export."""
    rows = []
    for key, values in pivot.items():
        row = {"key": key}
        row.update(values)
        rows.append(row)
    return rows


def consistent_keys(pivot: PivotTable) -> List[str]:
    """Return keys whose value is identical across all snapshots (None counts as missing)."""
    result = []
    for key, values in pivot.items():
        unique = set(values.values())
        if len(unique) == 1:
            result.append(key)
    return result


def divergent_keys(pivot: PivotTable) -> List[str]:
    """Return keys that differ in at least one snapshot."""
    result = []
    for key, values in pivot.items():
        unique = set(values.values())
        if len(unique) > 1:
            result.append(key)
    return result
