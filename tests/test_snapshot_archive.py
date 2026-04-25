"""Tests for envpack.snapshot_archive."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envpack.snapshot_archive import (
    ArchiveError,
    archive_snapshot,
    is_archived,
    list_archived,
    unarchive_snapshot,
)


@pytest.fixture()
def snap(tmp_path: Path) -> Path:
    p = tmp_path / "snap.json"
    p.write_text(json.dumps({"FOO": "bar"}), encoding="utf-8")
    return p


def test_archive_moves_file(snap: Path, tmp_path: Path) -> None:
    archive_dir = tmp_path / "archive"
    dest = archive_snapshot(snap, archive_dir)
    assert dest.exists()
    assert not snap.exists()


def test_archive_returns_correct_path(snap: Path, tmp_path: Path) -> None:
    archive_dir = tmp_path / "archive"
    dest = archive_snapshot(snap, archive_dir)
    assert dest == archive_dir / snap.name


def test_archive_creates_archive_dir(snap: Path, tmp_path: Path) -> None:
    archive_dir = tmp_path / "deep" / "archive"
    archive_snapshot(snap, archive_dir)
    assert archive_dir.exists()


def test_archive_missing_source_raises(tmp_path: Path) -> None:
    with pytest.raises(ArchiveError, match="not found"):
        archive_snapshot(tmp_path / "ghost.json", tmp_path / "archive")


def test_archive_duplicate_raises(snap: Path, tmp_path: Path) -> None:
    archive_dir = tmp_path / "archive"
    archive_dir.mkdir()
    (archive_dir / snap.name).write_text("{}", encoding="utf-8")
    with pytest.raises(ArchiveError, match="already contains"):
        archive_snapshot(snap, archive_dir)


def test_unarchive_restores_file(snap: Path, tmp_path: Path) -> None:
    archive_dir = tmp_path / "archive"
    dest_dir = tmp_path / "active"
    archive_snapshot(snap, archive_dir)
    restored = unarchive_snapshot(snap.name, dest_dir, archive_dir)
    assert restored.exists()
    assert not (archive_dir / snap.name).exists()


def test_unarchive_missing_raises(tmp_path: Path) -> None:
    with pytest.raises(ArchiveError, match="No archived snapshot"):
        unarchive_snapshot("ghost.json", tmp_path / "active", tmp_path / "archive")


def test_unarchive_no_overwrite_raises(snap: Path, tmp_path: Path) -> None:
    archive_dir = tmp_path / "archive"
    dest_dir = tmp_path / "active"
    dest_dir.mkdir()
    archive_snapshot(snap, archive_dir)
    (dest_dir / snap.name).write_text("{}", encoding="utf-8")
    with pytest.raises(ArchiveError, match="already exists"):
        unarchive_snapshot(snap.name, dest_dir, archive_dir)


def test_unarchive_overwrite_succeeds(snap: Path, tmp_path: Path) -> None:
    archive_dir = tmp_path / "archive"
    dest_dir = tmp_path / "active"
    dest_dir.mkdir()
    archive_snapshot(snap, archive_dir)
    (dest_dir / snap.name).write_text("{}", encoding="utf-8")
    restored = unarchive_snapshot(snap.name, dest_dir, archive_dir, overwrite=True)
    assert restored.exists()


def test_list_archived_empty(tmp_path: Path) -> None:
    assert list_archived(tmp_path / "archive") == []


def test_list_archived_returns_names(tmp_path: Path) -> None:
    archive_dir = tmp_path / "archive"
    archive_dir.mkdir()
    for name in ["b.json", "a.json", "c.json"]:
        (archive_dir / name).write_text("{}", encoding="utf-8")
    assert list_archived(archive_dir) == ["a.json", "b.json", "c.json"]


def test_is_archived_true(snap: Path, tmp_path: Path) -> None:
    archive_dir = tmp_path / "archive"
    archive_snapshot(snap, archive_dir)
    assert is_archived(snap.name, archive_dir) is True


def test_is_archived_false(tmp_path: Path) -> None:
    assert is_archived("missing.json", tmp_path / "archive") is False
