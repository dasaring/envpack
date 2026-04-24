"""Tests for envpack.snapshot_patch."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envpack.snapshot_patch import (
    PatchError,
    patch_file,
    rename_key,
    set_keys,
    unset_keys,
)


# ---------------------------------------------------------------------------
# unit tests for pure helpers
# ---------------------------------------------------------------------------

def test_set_keys_adds_new_key():
    result = set_keys({"A": "1"}, {"B": "2"})
    assert result == {"A": "1", "B": "2"}


def test_set_keys_overwrites_existing():
    result = set_keys({"A": "1"}, {"A": "99"})
    assert result["A"] == "99"


def test_set_keys_does_not_mutate_original():
    original = {"A": "1"}
    set_keys(original, {"B": "2"})
    assert "B" not in original


def test_unset_keys_removes_key():
    result = unset_keys({"A": "1", "B": "2"}, ["A"])
    assert "A" not in result
    assert result["B"] == "2"


def test_unset_keys_ignores_missing():
    result = unset_keys({"A": "1"}, ["MISSING"])
    assert result == {"A": "1"}


def test_rename_key_renames():
    result = rename_key({"OLD": "val", "X": "1"}, "OLD", "NEW")
    assert "OLD" not in result
    assert result["NEW"] == "val"
    assert result["X"] == "1"


def test_rename_key_missing_raises():
    with pytest.raises(PatchError, match="not found"):
        rename_key({"A": "1"}, "MISSING", "B")


def test_rename_key_existing_target_raises():
    with pytest.raises(PatchError, match="already exists"):
        rename_key({"A": "1", "B": "2"}, "A", "B")


def test_rename_key_overwrite_allowed():
    result = rename_key({"A": "1", "B": "2"}, "A", "B", overwrite=True)
    assert result["B"] == "1"
    assert "A" not in result


# ---------------------------------------------------------------------------
# integration tests for patch_file
# ---------------------------------------------------------------------------

@pytest.fixture()
def snap(tmp_path: Path) -> Path:
    p = tmp_path / "snap.json"
    p.write_text(json.dumps({"FOO": "bar", "BAZ": "qux"}))
    return p


def test_patch_file_set_in_place(snap: Path):
    patch_file(snap, set={"NEW": "value"})
    data = json.loads(snap.read_text())
    assert data["NEW"] == "value"


def test_patch_file_unset_in_place(snap: Path):
    patch_file(snap, unset=["FOO"])
    data = json.loads(snap.read_text())
    assert "FOO" not in data


def test_patch_file_rename_in_place(snap: Path):
    patch_file(snap, rename={"FOO": "FOO2"})
    data = json.loads(snap.read_text())
    assert "FOO" not in data
    assert data["FOO2"] == "bar"


def test_patch_file_writes_to_dest(snap: Path, tmp_path: Path):
    dest = tmp_path / "out.json"
    result = patch_file(snap, set={"X": "y"}, dest=dest)
    assert result == dest
    assert dest.exists()
    # original unchanged
    orig = json.loads(snap.read_text())
    assert "X" not in orig


def test_patch_file_rename_error_propagates(snap: Path):
    with pytest.raises(PatchError):
        patch_file(snap, rename={"NONEXISTENT": "OTHER"})
