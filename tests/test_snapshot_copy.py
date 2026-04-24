"""Tests for envpack.snapshot_copy."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envpack.snapshot_copy import CopyError, clone_snapshot, copy_snapshot


@pytest.fixture()
def snap(tmp_path: Path) -> Path:
    p = tmp_path / "snap.json"
    p.write_text(json.dumps({"HOME": "/home/user", "PATH": "/usr/bin", "SECRET": "s3cr3t"}))
    return p


def test_copy_creates_destination(snap: Path, tmp_path: Path) -> None:
    dest = tmp_path / "copy.json"
    result = copy_snapshot(snap, dest)
    assert result == dest.resolve()
    assert dest.exists()


def test_copy_content_matches_source(snap: Path, tmp_path: Path) -> None:
    dest = tmp_path / "copy.json"
    copy_snapshot(snap, dest)
    assert json.loads(dest.read_text()) == json.loads(snap.read_text())


def test_copy_include_keys(snap: Path, tmp_path: Path) -> None:
    dest = tmp_path / "filtered.json"
    copy_snapshot(snap, dest, include_keys=["HOME", "PATH"])
    data = json.loads(dest.read_text())
    assert set(data.keys()) == {"HOME", "PATH"}
    assert "SECRET" not in data


def test_copy_exclude_keys(snap: Path, tmp_path: Path) -> None:
    dest = tmp_path / "redacted.json"
    copy_snapshot(snap, dest, exclude_keys=["SECRET"])
    data = json.loads(dest.read_text())
    assert "SECRET" not in data
    assert "HOME" in data
    assert "PATH" in data


def test_copy_include_and_exclude_combined(snap: Path, tmp_path: Path) -> None:
    dest = tmp_path / "combo.json"
    copy_snapshot(snap, dest, include_keys=["HOME", "PATH", "SECRET"], exclude_keys=["SECRET"])
    data = json.loads(dest.read_text())
    assert "SECRET" not in data
    assert "HOME" in data


def test_copy_missing_source_raises(tmp_path: Path) -> None:
    with pytest.raises(CopyError, match="Source snapshot not found"):
        copy_snapshot(tmp_path / "missing.json", tmp_path / "dest.json")


def test_copy_no_overwrite_raises(snap: Path, tmp_path: Path) -> None:
    dest = tmp_path / "existing.json"
    dest.write_text("{}")
    with pytest.raises(CopyError, match="Destination already exists"):
        copy_snapshot(snap, dest)


def test_copy_overwrite_flag_replaces_file(snap: Path, tmp_path: Path) -> None:
    dest = tmp_path / "existing.json"
    dest.write_text("{}")
    copy_snapshot(snap, dest, overwrite=True)
    data = json.loads(dest.read_text())
    assert "HOME" in data


def test_clone_snapshot_copies_all_keys(snap: Path, tmp_path: Path) -> None:
    dest = tmp_path / "clone.json"
    clone_snapshot(snap, dest)
    assert json.loads(dest.read_text()) == json.loads(snap.read_text())


def test_copy_include_nonexistent_key_results_in_empty(snap: Path, tmp_path: Path) -> None:
    dest = tmp_path / "empty.json"
    copy_snapshot(snap, dest, include_keys=["DOES_NOT_EXIST"])
    assert json.loads(dest.read_text()) == {}
