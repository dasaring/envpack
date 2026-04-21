"""Tests for envpack.pin module."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envpack.pin import (
    pin_snapshot,
    unpin_snapshot,
    is_pinned,
    list_pins,
    clear_pins,
)


@pytest.fixture()
def pin_file(tmp_path: Path) -> Path:
    return tmp_path / "pins.json"


def test_pin_new_snapshot(pin_file: Path) -> None:
    result = pin_snapshot("snap_a.json", pin_file)
    assert result is True


def test_pin_creates_file(pin_file: Path) -> None:
    pin_snapshot("snap_a.json", pin_file)
    assert pin_file.exists()


def test_pin_file_is_valid_json(pin_file: Path) -> None:
    pin_snapshot("snap_a.json", pin_file)
    data = json.loads(pin_file.read_text())
    assert isinstance(data, list)


def test_pin_already_pinned_returns_false(pin_file: Path) -> None:
    pin_snapshot("snap_a.json", pin_file)
    result = pin_snapshot("snap_a.json", pin_file)
    assert result is False


def test_pin_no_duplicates(pin_file: Path) -> None:
    pin_snapshot("snap_a.json", pin_file)
    pin_snapshot("snap_a.json", pin_file)
    assert list_pins(pin_file).count("snap_a.json") == 1


def test_unpin_existing(pin_file: Path) -> None:
    pin_snapshot("snap_a.json", pin_file)
    result = unpin_snapshot("snap_a.json", pin_file)
    assert result is True
    assert "snap_a.json" not in list_pins(pin_file)


def test_unpin_nonexistent_returns_false(pin_file: Path) -> None:
    result = unpin_snapshot("ghost.json", pin_file)
    assert result is False


def test_is_pinned_true(pin_file: Path) -> None:
    pin_snapshot("snap_b.json", pin_file)
    assert is_pinned("snap_b.json", pin_file) is True


def test_is_pinned_false(pin_file: Path) -> None:
    assert is_pinned("snap_b.json", pin_file) is False


def test_list_pins_empty(pin_file: Path) -> None:
    assert list_pins(pin_file) == []


def test_list_pins_multiple(pin_file: Path) -> None:
    pin_snapshot("a.json", pin_file)
    pin_snapshot("b.json", pin_file)
    pins = list_pins(pin_file)
    assert "a.json" in pins
    assert "b.json" in pins
    assert len(pins) == 2


def test_clear_pins_returns_count(pin_file: Path) -> None:
    pin_snapshot("a.json", pin_file)
    pin_snapshot("b.json", pin_file)
    count = clear_pins(pin_file)
    assert count == 2


def test_clear_pins_empties_list(pin_file: Path) -> None:
    pin_snapshot("a.json", pin_file)
    clear_pins(pin_file)
    assert list_pins(pin_file) == []
