"""Flatten nested environment variable prefixes into grouped sub-snapshots."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


class FlattenError(Exception):
    """Raised when flattening fails."""


def group_by_prefix(snapshot: Dict[str, str], sep: str = "_") -> Dict[str, Dict[str, str]]:
    """Group snapshot keys by their first prefix segment.

    Keys without a separator go into the special '__root__' group.
    """
    groups: Dict[str, Dict[str, str]] = {}
    for key, value in snapshot.items():
        if sep in key:
            prefix, _, rest = key.partition(sep)
        else:
            prefix = "__root__"
            rest = key
        groups.setdefault(prefix, {})[rest] = value
    return groups


def flatten_groups(groups: Dict[str, Dict[str, str]], sep: str = "_") -> Dict[str, str]:
    """Reverse of group_by_prefix: merge grouped dicts back into a flat snapshot."""
    flat: Dict[str, str] = {}
    for prefix, keys in groups.items():
        for key, value in keys.items():
            if prefix == "__root__":
                flat[key] = value
            else:
                flat[f"{prefix}{sep}{key}"] = value
    return flat


def prefix_keys(snapshot: Dict[str, str], prefix: str, sep: str = "_") -> Dict[str, str]:
    """Add a prefix to every key in the snapshot."""
    if not prefix:
        raise FlattenError("prefix must be a non-empty string")
    return {f"{prefix}{sep}{k}": v for k, v in snapshot.items()}


def strip_prefix(snapshot: Dict[str, str], prefix: str, sep: str = "_") -> Dict[str, str]:
    """Remove a leading prefix from all matching keys; non-matching keys are dropped."""
    if not prefix:
        raise FlattenError("prefix must be a non-empty string")
    full_prefix = f"{prefix}{sep}"
    return {
        k[len(full_prefix):]: v
        for k, v in snapshot.items()
        if k.startswith(full_prefix)
    }


def save_groups(groups: Dict[str, Dict[str, str]], output_dir: Path) -> List[Path]:
    """Write each group as a separate JSON snapshot file under *output_dir*."""
    output_dir.mkdir(parents=True, exist_ok=True)
    saved: List[Path] = []
    for name, data in groups.items():
        dest = output_dir / f"{name}.json"
        dest.write_text(json.dumps(data, indent=2, sort_keys=True))
        saved.append(dest)
    return saved
