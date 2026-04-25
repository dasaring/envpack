"""Filter snapshots by tag combinations (union, intersection, exclusion)."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from envpack.tags import get_snapshots_by_tag, _load_tags


class TagFilterError(Exception):
    """Raised when a tag filter operation fails."""


def snapshots_with_any_tag(tags: List[str], tags_file: Optional[Path] = None) -> List[str]:
    """Return snapshot paths that have at least one of the given tags (union)."""
    if not tags:
        return []
    seen: set[str] = set()
    result: List[str] = []
    for tag in tags:
        for path in get_snapshots_by_tag(tag, tags_file=tags_file):
            if path not in seen:
                seen.add(path)
                result.append(path)
    return result


def snapshots_with_all_tags(tags: List[str], tags_file: Optional[Path] = None) -> List[str]:
    """Return snapshot paths that have ALL of the given tags (intersection)."""
    if not tags:
        return []
    sets = [set(get_snapshots_by_tag(t, tags_file=tags_file)) for t in tags]
    common = sets[0].intersection(*sets[1:])
    return sorted(common)


def snapshots_excluding_tags(tags: List[str], tags_file: Optional[Path] = None) -> List[str]:
    """Return all known snapshot paths that have NONE of the given tags."""
    data = _load_tags(tags_file)
    excluded: set[str] = set()
    for tag in tags:
        excluded.update(data.get(tag, []))
    all_paths: set[str] = set()
    for paths in data.values():
        all_paths.update(paths)
    return sorted(all_paths - excluded)


def filter_snapshots(
    *,
    any_tags: Optional[List[str]] = None,
    all_tags: Optional[List[str]] = None,
    exclude_tags: Optional[List[str]] = None,
    tags_file: Optional[Path] = None,
) -> List[str]:
    """Combine any/all/exclude filters and return matching snapshot paths."""
    candidates: Optional[set[str]] = None

    if any_tags:
        union = set(snapshots_with_any_tag(any_tags, tags_file=tags_file))
        candidates = union if candidates is None else candidates & union

    if all_tags:
        intersection = set(snapshots_with_all_tags(all_tags, tags_file=tags_file))
        candidates = intersection if candidates is None else candidates & intersection

    if candidates is None:
        data = _load_tags(tags_file)
        candidates = set(p for paths in data.values() for p in paths)

    if exclude_tags:
        excluded = set(snapshots_excluding_tags(exclude_tags, tags_file=tags_file))
        # excluded already excludes those tags; intersect to keep only non-excluded
        excluded_set = set()
        for t in exclude_tags:
            excluded_set.update(get_snapshots_by_tag(t, tags_file=tags_file))
        candidates -= excluded_set

    return sorted(candidates)
