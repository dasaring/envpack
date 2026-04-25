"""Tests for envpack.cli_snapshot_archive."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pytest

from envpack.cli_snapshot_archive import (
    cmd_archive,
    cmd_archive_check,
    cmd_archive_list,
    cmd_unarchive,
)


@pytest.fixture()
def snap(tmp_path: Path) -> Path:
    p = tmp_path / "env.json"
    p.write_text(json.dumps({"KEY": "val"}), encoding="utf-8")
    return p


def make_args(**kwargs) -> argparse.Namespace:
    defaults = {"archive_dir": ".envpack_archive", "overwrite": False}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_archive_prints_path(snap: Path, tmp_path: Path, capsys) -> None:
    args = make_args(snapshot=str(snap), archive_dir=str(tmp_path / "arch"))
    cmd_archive(args)
    out = capsys.readouterr().out
    assert "Archived:" in out
    assert "env.json" in out


def test_cmd_archive_missing_snapshot_exits_1(tmp_path: Path) -> None:
    args = make_args(snapshot=str(tmp_path / "ghost.json"), archive_dir=str(tmp_path / "arch"))
    with pytest.raises(SystemExit) as exc:
        cmd_archive(args)
    assert exc.value.code == 1


def test_cmd_unarchive_prints_restored(snap: Path, tmp_path: Path, capsys) -> None:
    arch = tmp_path / "arch"
    active = tmp_path / "active"
    # first archive it
    arch_args = make_args(snapshot=str(snap), archive_dir=str(arch))
    cmd_archive(arch_args)
    capsys.readouterr()  # clear

    un_args = make_args(name=snap.name, dest_dir=str(active), archive_dir=str(arch))
    cmd_unarchive(un_args)
    out = capsys.readouterr().out
    assert "Restored:" in out


def test_cmd_unarchive_missing_exits_1(tmp_path: Path) -> None:
    args = make_args(name="ghost.json", dest_dir=str(tmp_path), archive_dir=str(tmp_path / "arch"))
    with pytest.raises(SystemExit) as exc:
        cmd_unarchive(args)
    assert exc.value.code == 1


def test_cmd_archive_list_empty(tmp_path: Path, capsys) -> None:
    args = make_args(archive_dir=str(tmp_path / "arch"))
    cmd_archive_list(args)
    out = capsys.readouterr().out
    assert "No archived" in out


def test_cmd_archive_list_shows_names(snap: Path, tmp_path: Path, capsys) -> None:
    arch = tmp_path / "arch"
    cmd_archive(make_args(snapshot=str(snap), archive_dir=str(arch)))
    capsys.readouterr()
    cmd_archive_list(make_args(archive_dir=str(arch)))
    out = capsys.readouterr().out
    assert snap.name in out


def test_cmd_archive_check_found(snap: Path, tmp_path: Path, capsys) -> None:
    arch = tmp_path / "arch"
    cmd_archive(make_args(snapshot=str(snap), archive_dir=str(arch)))
    capsys.readouterr()
    cmd_archive_check(make_args(name=snap.name, archive_dir=str(arch)))
    out = capsys.readouterr().out
    assert "is archived" in out


def test_cmd_archive_check_not_found_exits_1(tmp_path: Path) -> None:
    args = make_args(name="ghost.json", archive_dir=str(tmp_path / "arch"))
    with pytest.raises(SystemExit) as exc:
        cmd_archive_check(args)
    assert exc.value.code == 1
