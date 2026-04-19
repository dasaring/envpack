"""Tag snapshots with labels for easier organization and retrieval."""

import json
from pathlib import Path
from typing import Dict, List, Optional

DEFAULT_TAGS_FILE = Path.home() / ".envpack" / "tags.json"


def _load_tags(tags_file: Path = DEFAULT_TAGS_FILE) -> Dict[str, List[str]]:
    """Load tag mappings from disk. Returns dict of tag -> [snapshot_paths]."""
    if not tags_file.exists():
        return {}
    with tags_file.open("r") as f:
        return json.load(f)


def _save_tags(data: Dict[str, List[str]], tags_file: Path = DEFAULT_TAGS_FILE) -> None:
    """Persist tag mappings to disk."""
    tags_file.parent.mkdir(parents=True, exist_ok=True)
    with tags_file.open("w") as f:
        json.dump(data, f, indent=2)


def add_tag(snapshot_path: str, tag: str, tags_file: Path = DEFAULT_TAGS_FILE) -> None:
    """Associate a tag with a snapshot path."""
    data = _load_tags(tags_file)
    if tag not in data:
        data[tag] = []
    if snapshot_path not in data[tag]:
        data[tag].append(snapshot_path)
    _save_tags(data, tags_file)


def remove_tag(snapshot_path: str, tag: str, tags_file: Path = DEFAULT_TAGS_FILE) -> bool:
    """Remove a tag from a snapshot. Returns True if removed, False if not found."""
    data = _load_tags(tags_file)
    if tag not in data or snapshot_path not in data[tag]:
        return False
    data[tag].remove(snapshot_path)
    if not data[tag]:
        del data[tag]
    _save_tags(data, tags_file)
    return True


def get_snapshots_by_tag(tag: str, tags_file: Path = DEFAULT_TAGS_FILE) -> List[str]:
    """Return all snapshot paths associated with a tag."""
    data = _load_tags(tags_file)
    return data.get(tag, [])


def get_tags_for_snapshot(snapshot_path: str, tags_file: Path = DEFAULT_TAGS_FILE) -> List[str]:
    """Return all tags associated with a given snapshot path."""
    data = _load_tags(tags_file)
    return [tag for tag, paths in data.items() if snapshot_path in paths]


def list_all_tags(tags_file: Path = DEFAULT_TAGS_FILE) -> Dict[str, List[str]]:
    """Return the full tag mapping."""
    return _load_tags(tags_file)
