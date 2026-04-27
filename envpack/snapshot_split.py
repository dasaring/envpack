"""Split a snapshot into multiple smaller snapshots by prefix or key list."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from envpack.snapshot import load, save


class SplitError(Exception):
    """Raised when a split operation cannot be completed."""


def split_by_prefix(
    snapshot: Dict[str, str],
    prefixes: List[str],
    strip_prefix: bool = False,
) -> Dict[str, Dict[str, str]]:
    """Partition snapshot keys into groups by prefix.

    Keys that match no prefix land in an ``"_other"`` bucket.
    """
    result: Dict[str, Dict[str, str]] = {p: {} for p in prefixes}
    result["_other"] = {}

    for key, value in snapshot.items():
        matched = False
        for prefix in prefixes:
            if key.startswith(prefix):
                out_key = key[len(prefix):] if strip_prefix else key
                result[prefix][out_key] = value
                matched = True
                break
        if not matched:
            result["_other"][key] = value

    return result


def split_by_keys(
    snapshot: Dict[str, str],
    groups: Dict[str, List[str]],
) -> Dict[str, Dict[str, str]]:
    """Partition snapshot into named groups by explicit key lists.

    Keys not listed in any group go into ``"_other"``.
    """
    assigned: set = set()
    result: Dict[str, Dict[str, str]] = {name: {} for name in groups}
    result["_other"] = {}

    for group_name, keys in groups.items():
        for key in keys:
            if key in snapshot:
                result[group_name][key] = snapshot[key]
                assigned.add(key)

    for key, value in snapshot.items():
        if key not in assigned:
            result["_other"][key] = value

    return result


def save_split(
    parts: Dict[str, Dict[str, str]],
    output_dir: Path,
    base_name: str = "split",
    skip_empty: bool = True,
) -> Dict[str, Path]:
    """Write each part to ``<output_dir>/<base_name>_<group>.json``.

    Returns a mapping of group name -> written path.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    written: Dict[str, Path] = {}
    for group_name, data in parts.items():
        if skip_empty and not data:
            continue
        dest = output_dir / f"{base_name}_{group_name}.json"
        save(data, dest)
        written[group_name] = dest

    return written
