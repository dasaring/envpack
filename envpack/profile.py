"""Profile management: named collections of snapshot paths for different environments."""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional

DEFAULT_PROFILES_FILE = Path.home() / ".envpack" / "profiles.json"


def _load_profiles(profiles_file: Path) -> Dict[str, List[str]]:
    if not profiles_file.exists():
        return {}
    with profiles_file.open("r") as fh:
        return json.load(fh)


def _save_profiles(profiles: Dict[str, List[str]], profiles_file: Path) -> None:
    profiles_file.parent.mkdir(parents=True, exist_ok=True)
    with profiles_file.open("w") as fh:
        json.dump(profiles, fh, indent=2)


def create_profile(
    name: str,
    snapshot_paths: Optional[List[str]] = None,
    profiles_file: Path = DEFAULT_PROFILES_FILE,
) -> Dict[str, List[str]]:
    """Create or overwrite a named profile with the given snapshot paths."""
    profiles = _load_profiles(profiles_file)
    profiles[name] = list(snapshot_paths or [])
    _save_profiles(profiles, profiles_file)
    return profiles[name]


def delete_profile(
    name: str,
    profiles_file: Path = DEFAULT_PROFILES_FILE,
) -> bool:
    """Delete a profile by name. Returns True if it existed, False otherwise."""
    profiles = _load_profiles(profiles_file)
    if name not in profiles:
        return False
    del profiles[name]
    _save_profiles(profiles, profiles_file)
    return True


def add_snapshot_to_profile(
    name: str,
    snapshot_path: str,
    profiles_file: Path = DEFAULT_PROFILES_FILE,
) -> List[str]:
    """Append a snapshot path to an existing or new profile."""
    profiles = _load_profiles(profiles_file)
    entry = profiles.setdefault(name, [])
    if snapshot_path not in entry:
        entry.append(snapshot_path)
    _save_profiles(profiles, profiles_file)
    return entry


def get_profile(
    name: str,
    profiles_file: Path = DEFAULT_PROFILES_FILE,
) -> Optional[List[str]]:
    """Return the list of snapshot paths for a profile, or None if not found."""
    profiles = _load_profiles(profiles_file)
    return profiles.get(name)


def list_profiles(
    profiles_file: Path = DEFAULT_PROFILES_FILE,
) -> List[str]:
    """Return all profile names."""
    return list(_load_profiles(profiles_file).keys())
