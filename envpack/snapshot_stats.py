"""Compute statistics over a collection of snapshot files."""

from __future__ import annotations

import os
import statistics
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envpack.snapshot import load


@dataclass
class SnapshotStats:
    count: int
    total_keys: int
    avg_keys: float
    min_keys: int
    max_keys: int
    common_keys: List[str]
    unique_keys: List[str]
    key_frequency: Dict[str, int] = field(default_factory=dict)

    def summary(self) -> str:
        lines = [
            f"Snapshots analysed : {self.count}",
            f"Total keys         : {self.total_keys}",
            f"Avg keys/snapshot  : {self.avg_keys:.1f}",
            f"Min keys           : {self.min_keys}",
            f"Max keys           : {self.max_keys}",
            f"Common keys        : {len(self.common_keys)}",
            f"Unique keys        : {len(self.unique_keys)}",
        ]
        return "\n".join(lines)


def compute_stats(snapshot_files: List[str]) -> Optional[SnapshotStats]:
    """Return statistics for a list of snapshot file paths.

    Returns None if *snapshot_files* is empty.
    """
    if not snapshot_files:
        return None

    snapshots = []
    for path in snapshot_files:
        try:
            snapshots.append(load(path))
        except (OSError, ValueError):
            continue

    if not snapshots:
        return None

    key_counts = [len(s) for s in snapshots]
    freq: Dict[str, int] = {}
    for snap in snapshots:
        for k in snap:
            freq[k] = freq.get(k, 0) + 1

    n = len(snapshots)
    common = [k for k, v in freq.items() if v == n]
    unique = [k for k, v in freq.items() if v == 1]

    return SnapshotStats(
        count=n,
        total_keys=sum(key_counts),
        avg_keys=statistics.mean(key_counts),
        min_keys=min(key_counts),
        max_keys=max(key_counts),
        common_keys=sorted(common),
        unique_keys=sorted(unique),
        key_frequency=freq,
    )


def stats_from_directory(directory: str) -> Optional[SnapshotStats]:
    """Compute stats for all *.json snapshot files in *directory*."""
    if not os.path.isdir(directory):
        raise NotADirectoryError(f"{directory!r} is not a directory")
    files = [
        os.path.join(directory, f)
        for f in sorted(os.listdir(directory))
        if f.endswith(".json")
    ]
    return compute_stats(files)
