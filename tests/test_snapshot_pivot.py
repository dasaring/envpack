"""Tests for envpack.snapshot_pivot."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envpack.snapshot_pivot import (
    PivotError,
    build_pivot,
    consistent_keys,
    divergent_keys,
    pivot_to_rows,
)


@pytest.fixture()
def snap_dir(tmp_path: Path):
    def _write(name: str, data: dict) -> Path:
        p = tmp_path / name
        p.write_text(json.dumps(data))
        return p

    return _write


def test_build_pivot_empty_list_raises():
    with pytest.raises(PivotError, match="At least one"):
        build_pivot([])


def test_build_pivot_missing_file_raises(tmp_path):
    with pytest.raises(PivotError, match="not found"):
        build_pivot([tmp_path / "ghost.json"])


def test_build_pivot_single_snapshot(snap_dir):
    p = snap_dir("a.json", {"FOO": "bar"})
    pivot = build_pivot([p])
    assert "FOO" in pivot
    assert pivot["FOO"]["a.json"] == "bar"


def test_build_pivot_all_keys_present(snap_dir):
    a = snap_dir("a.json", {"X": "1", "Y": "2"})
    b = snap_dir("b.json", {"X": "1", "Z": "3"})
    pivot = build_pivot([a, b])
    assert set(pivot.keys()) == {"X", "Y", "Z"}


def test_build_pivot_missing_key_is_none(snap_dir):
    a = snap_dir("a.json", {"X": "1"})
    b = snap_dir("b.json", {"Y": "2"})
    pivot = build_pivot([a, b])
    assert pivot["X"]["b.json"] is None
    assert pivot["Y"]["a.json"] is None


def test_pivot_to_rows_includes_key_field(snap_dir):
    p = snap_dir("s.json", {"A": "1"})
    pivot = build_pivot([p])
    rows = pivot_to_rows(pivot)
    assert rows[0]["key"] == "A"
    assert rows[0]["s.json"] == "1"


def test_consistent_keys_identical_values(snap_dir):
    a = snap_dir("a.json", {"SAME": "yes", "DIFF": "1"})
    b = snap_dir("b.json", {"SAME": "yes", "DIFF": "2"})
    pivot = build_pivot([a, b])
    assert "SAME" in consistent_keys(pivot)
    assert "DIFF" not in consistent_keys(pivot)


def test_divergent_keys_detects_difference(snap_dir):
    a = snap_dir("a.json", {"PORT": "8000"})
    b = snap_dir("b.json", {"PORT": "9000"})
    pivot = build_pivot([a, b])
    assert "PORT" in divergent_keys(pivot)


def test_divergent_keys_missing_counts_as_different(snap_dir):
    a = snap_dir("a.json", {"ONLY_A": "val"})
    b = snap_dir("b.json", {})
    pivot = build_pivot([a, b])
    assert "ONLY_A" in divergent_keys(pivot)


def test_pivot_keys_are_sorted(snap_dir):
    p = snap_dir("s.json", {"Z": "1", "A": "2", "M": "3"})
    pivot = build_pivot([p])
    assert list(pivot.keys()) == sorted(pivot.keys())
