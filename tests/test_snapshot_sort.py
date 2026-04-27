"""Tests for envpack.snapshot_sort."""
from __future__ import annotations

import json
import pytest

from envpack.snapshot_sort import SortError, _natural_key, sort_snapshot, sort_file


# ---------------------------------------------------------------------------
# sort_snapshot
# ---------------------------------------------------------------------------

def test_alpha_sorts_case_insensitive():
    snap = {"ZEBRA": "1", "apple": "2", "Mango": "3"}
    result = sort_snapshot(snap, strategy="alpha")
    assert list(result.keys()) == ["apple", "Mango", "ZEBRA"]


def test_alpha_desc_reverses_order():
    snap = {"apple": "1", "Mango": "2", "ZEBRA": "3"}
    result = sort_snapshot(snap, strategy="alpha_desc")
    assert list(result.keys()) == ["ZEBRA", "Mango", "apple"]


def test_length_sorts_by_key_length():
    snap = {"AB": "1", "ABCDE": "2", "ABC": "3"}
    result = sort_snapshot(snap, strategy="length")
    assert list(result.keys()) == ["AB", "ABC", "ABCDE"]


def test_length_desc_sorts_longest_first():
    snap = {"AB": "1", "ABCDE": "2", "ABC": "3"}
    result = sort_snapshot(snap, strategy="length_desc")
    assert list(result.keys()) == ["ABCDE", "ABC", "AB"]


def test_natural_sort_handles_numbers():
    snap = {"KEY10": "a", "KEY2": "b", "KEY1": "c"}
    result = sort_snapshot(snap, strategy="natural")
    assert list(result.keys()) == ["KEY1", "KEY2", "KEY10"]


def test_invalid_strategy_raises():
    with pytest.raises(SortError, match="Unknown sort strategy"):
        sort_snapshot({"A": "1"}, strategy="bogus")


def test_does_not_mutate_original():
    snap = {"B": "2", "A": "1"}
    original_keys = list(snap.keys())
    sort_snapshot(snap, strategy="alpha")
    assert list(snap.keys()) == original_keys


def test_values_are_preserved():
    snap = {"Z": "last", "A": "first"}
    result = sort_snapshot(snap, strategy="alpha")
    assert result["A"] == "first"
    assert result["Z"] == "last"


def test_partial_keys_sorts_subset_appends_remainder():
    snap = {"C": "3", "A": "1", "B": "2", "D": "4"}
    result = sort_snapshot(snap, strategy="alpha", keys=["C", "A"])
    sorted_part = list(result.keys())[:2]
    remainder = list(result.keys())[2:]
    assert sorted_part == ["A", "C"]
    # B and D should appear after in original relative order
    assert set(remainder) == {"B", "D"}


def test_empty_snapshot_returns_empty():
    assert sort_snapshot({}) == {}


# ---------------------------------------------------------------------------
# sort_file
# ---------------------------------------------------------------------------

def test_sort_file_writes_sorted_json(tmp_path):
    snap = {"Z": "26", "A": "1", "M": "13"}
    p = tmp_path / "snap.json"
    p.write_text(json.dumps(snap))
    sort_file(str(p), strategy="alpha")
    loaded = json.loads(p.read_text())
    assert list(loaded.keys()) == ["A", "M", "Z"]


def test_sort_file_returns_path(tmp_path):
    p = tmp_path / "snap.json"
    p.write_text(json.dumps({"B": "2", "A": "1"}))
    returned = sort_file(str(p))
    assert returned == str(p)
