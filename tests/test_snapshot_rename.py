"""Tests for envpack.snapshot_rename."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envpack.snapshot_rename import RenameError, rename_snapshot, safe_rename


@pytest.fixture()
def snap(tmp_path: Path) -> Path:
    """Write a minimal snapshot file and return its path."""
    p = tmp_path / "env_snap.json"
    p.write_text(json.dumps({"KEY": "value"}), encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# rename_snapshot
# ---------------------------------------------------------------------------

def test_rename_moves_file(snap: Path, tmp_path: Path) -> None:
    dest = tmp_path / "renamed.json"
    result = rename_snapshot(snap, dest)
    assert result == dest.resolve()
    assert dest.exists()
    assert not snap.exists()


def test_rename_preserves_content(snap: Path, tmp_path: Path) -> None:
    dest = tmp_path / "copy.json"
    rename_snapshot(snap, dest)
    data = json.loads(dest.read_text(encoding="utf-8"))
    assert data == {"KEY": "value"}


def test_rename_creates_parent_dirs(snap: Path, tmp_path: Path) -> None:
    dest = tmp_path / "subdir" / "nested" / "env.json"
    rename_snapshot(snap, dest)
    assert dest.exists()


def test_rename_missing_source_raises(tmp_path: Path) -> None:
    with pytest.raises(RenameError, match="Source snapshot not found"):
        rename_snapshot(tmp_path / "ghost.json", tmp_path / "dest.json")


def test_rename_source_is_directory_raises(tmp_path: Path) -> None:
    d = tmp_path / "adir"
    d.mkdir()
    with pytest.raises(RenameError, match="not a file"):
        rename_snapshot(d, tmp_path / "dest.json")


def test_rename_dest_exists_no_overwrite_raises(snap: Path, tmp_path: Path) -> None:
    dest = tmp_path / "existing.json"
    dest.write_text("{}")
    with pytest.raises(RenameError, match="Destination already exists"):
        rename_snapshot(snap, dest)


def test_rename_dest_exists_overwrite_succeeds(snap: Path, tmp_path: Path) -> None:
    dest = tmp_path / "existing.json"
    dest.write_text("{}")
    result = rename_snapshot(snap, dest, overwrite=True)
    assert result == dest.resolve()
    data = json.loads(dest.read_text(encoding="utf-8"))
    assert data == {"KEY": "value"}


# ---------------------------------------------------------------------------
# safe_rename
# ---------------------------------------------------------------------------

def test_safe_rename_returns_true_on_success(snap: Path, tmp_path: Path) -> None:
    dest = tmp_path / "ok.json"
    ok, msg = safe_rename(snap, dest)
    assert ok is True
    assert str(dest.resolve()) == msg


def test_safe_rename_returns_false_on_failure(tmp_path: Path) -> None:
    ok, msg = safe_rename(tmp_path / "missing.json", tmp_path / "dest.json")
    assert ok is False
    assert "Source snapshot not found" in msg
