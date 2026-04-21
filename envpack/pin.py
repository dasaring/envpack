"""Pin management: mark specific snapshot files as pinned to prevent accidental overwrite or deletion."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

_DEFAULT_PIN_FILE = Path(".envpack_pins.json")


def _load_pins(pin_file: Path) -> List[str]:
    if not pin_file.exists():
        return []
    with pin_file.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    return data if isinstance(data, list) else []


def _save_pins(pins: List[str], pin_file: Path) -> None:
    with pin_file.open("w", encoding="utf-8") as fh:
        json.dump(pins, fh, indent=2)


def pin_snapshot(snapshot_path: str, pin_file: Path = _DEFAULT_PIN_FILE) -> bool:
    """Pin a snapshot. Returns True if newly pinned, False if already pinned."""
    pins = _load_pins(pin_file)
    if snapshot_path in pins:
        return False
    pins.append(snapshot_path)
    _save_pins(pins, pin_file)
    return True


def unpin_snapshot(snapshot_path: str, pin_file: Path = _DEFAULT_PIN_FILE) -> bool:
    """Unpin a snapshot. Returns True if removed, False if it wasn't pinned."""
    pins = _load_pins(pin_file)
    if snapshot_path not in pins:
        return False
    pins.remove(snapshot_path)
    _save_pins(pins, pin_file)
    return True


def is_pinned(snapshot_path: str, pin_file: Path = _DEFAULT_PIN_FILE) -> bool:
    """Return True if the given snapshot path is currently pinned."""
    return snapshot_path in _load_pins(pin_file)


def list_pins(pin_file: Path = _DEFAULT_PIN_FILE) -> List[str]:
    """Return all currently pinned snapshot paths."""
    return _load_pins(pin_file)


def clear_pins(pin_file: Path = _DEFAULT_PIN_FILE) -> int:
    """Remove all pins. Returns the number of pins cleared."""
    pins = _load_pins(pin_file)
    count = len(pins)
    _save_pins([], pin_file)
    return count
