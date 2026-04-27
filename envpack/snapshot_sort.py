"""Sort snapshot keys by various criteria."""
from __future__ import annotations

import re
from typing import Dict, List, Optional

Snapshot = Dict[str, str]


class SortError(Exception):
    """Raised when an invalid sort strategy is requested."""


_STRATEGIES = ("alpha", "alpha_desc", "length", "length_desc", "natural")


def _natural_key(s: str) -> List:
    """Key function for natural (human) sort order."""
    parts = re.split(r"(\d+)", s)
    return [int(p) if p.isdigit() else p.lower() for p in parts]


def sort_snapshot(
    snapshot: Snapshot,
    strategy: str = "alpha",
    keys: Optional[List[str]] = None,
) -> Snapshot:
    """Return a new snapshot with keys ordered by *strategy*.

    Parameters
    ----------
    snapshot:
        The source snapshot dict.
    strategy:
        One of ``alpha``, ``alpha_desc``, ``length``, ``length_desc``,
        ``natural``.
    keys:
        If provided, only sort the listed keys; the rest are appended at the
        end in their original order.
    """
    if strategy not in _STRATEGIES:
        raise SortError(
            f"Unknown sort strategy {strategy!r}. "
            f"Valid options: {', '.join(_STRATEGIES)}"
        )

    all_keys = list(snapshot.keys())
    sort_pool = [k for k in all_keys if keys is None or k in keys]
    remainder = [k for k in all_keys if k not in sort_pool]

    if strategy == "alpha":
        sorted_keys = sorted(sort_pool, key=str.lower)
    elif strategy == "alpha_desc":
        sorted_keys = sorted(sort_pool, key=str.lower, reverse=True)
    elif strategy == "length":
        sorted_keys = sorted(sort_pool, key=len)
    elif strategy == "length_desc":
        sorted_keys = sorted(sort_pool, key=len, reverse=True)
    else:  # natural
        sorted_keys = sorted(sort_pool, key=_natural_key)

    ordered = sorted_keys + remainder
    return {k: snapshot[k] for k in ordered}


def sort_file(path: str, strategy: str = "alpha", keys=None) -> str:
    """Sort the snapshot stored at *path* in-place and return the path."""
    import json
    from pathlib import Path

    p = Path(path)
    data = json.loads(p.read_text())
    sorted_data = sort_snapshot(data, strategy=strategy, keys=keys)
    p.write_text(json.dumps(sorted_data, indent=2))
    return str(p)
