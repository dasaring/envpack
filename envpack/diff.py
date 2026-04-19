"""Diff two environment snapshots and report added, removed, and changed keys."""

from typing import Dict, NamedTuple


class DiffResult(NamedTuple):
    added: Dict[str, str]
    removed: Dict[str, str]
    changed: Dict[str, tuple]  # key -> (old_value, new_value)

    def is_empty(self) -> bool:
        return not (self.added or self.removed or self.changed)

    def summary(self) -> str:
        lines = []
        for key, value in sorted(self.added.items()):
            lines.append(f"+ {key}={value}")
        for key, value in sorted(self.removed.items()):
            lines.append(f"- {key}={value}")
        for key, (old, new) in sorted(self.changed.items()):
            lines.append(f"~ {key}: {old!r} -> {new!r}")
        return "\n".join(lines) if lines else "(no differences)"

    def to_dict(self) -> Dict[str, object]:
        """Return a plain dict representation suitable for serialisation."""
        return {
            "added": dict(self.added),
            "removed": dict(self.removed),
            "changed": {k: list(v) for k, v in self.changed.items()},
        }


def diff_snapshots(before: Dict[str, str], after: Dict[str, str]) -> DiffResult:
    """Compare two snapshots and return a DiffResult.

    Args:
        before: The earlier snapshot dict.
        after: The later snapshot dict.

    Returns:
        DiffResult with added, removed, and changed entries.
    """
    before_keys = set(before)
    after_keys = set(after)

    added = {k: after[k] for k in after_keys - before_keys}
    removed = {k: before[k] for k in before_keys - after_keys}
    changed = {
        k: (before[k], after[k])
        for k in before_keys & after_keys
        if before[k] != after[k]
    }

    return DiffResult(added=added, removed=removed, changed=changed)
