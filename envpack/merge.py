"""Merge multiple snapshots into one, with configurable conflict resolution."""

from typing import Dict, List, Optional

Strategy = str  # 'first', 'last', 'error'


class MergeConflictError(Exception):
    """Raised when conflicting keys are found and strategy='error'."""

    def __init__(self, conflicts: Dict[str, List[str]]):
        self.conflicts = conflicts
        keys = ", ".join(conflicts.keys())
        super().__init__(f"Merge conflicts on keys: {keys}")


def merge_snapshots(
    snapshots: List[Dict[str, str]],
    strategy: Strategy = "last",
    labels: Optional[List[str]] = None,
) -> Dict[str, str]:
    """Merge a list of snapshots into a single dict.

    Args:
        snapshots: ordered list of env-var dicts.
        strategy: how to handle key conflicts.
            'first' — keep value from first snapshot that defines the key.
            'last'  — keep value from last snapshot (default).
            'error' — raise MergeConflictError listing all conflicting keys.
        labels: optional names for each snapshot (used in error messages).

    Returns:
        Merged snapshot dict.
    """
    if not snapshots:
        return {}

    if labels and len(labels) != len(snapshots):
        raise ValueError("labels length must match snapshots length")

    if strategy == "error":
        conflicts: Dict[str, List[str]] = {}
        seen: Dict[str, int] = {}
        for idx, snap in enumerate(snapshots):
            for key in snap:
                if key in seen:
                    label_a = labels[seen[key]] if labels else str(seen[key])
                    label_b = labels[idx] if labels else str(idx)
                    conflicts.setdefault(key, [label_a])
                    if label_b not in conflicts[key]:
                        conflicts[key].append(label_b)
                else:
                    seen[key] = idx
        if conflicts:
            raise MergeConflictError(conflicts)
        result: Dict[str, str] = {}
        for snap in snapshots:
            result.update(snap)
        return result

    result = {}
    for snap in snapshots:
        for key, value in snap.items():
            if strategy == "first" and key in result:
                continue
            result[key] = value
    return result
