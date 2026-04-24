"""Tests for envpack.cli_snapshot_patch."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pytest

from envpack.cli_snapshot_patch import cmd_patch, register_patch_commands


@pytest.fixture()
def snap(tmp_path: Path) -> Path:
    p = tmp_path / "env.json"
    p.write_text(json.dumps({"FOO": "bar", "BAZ": "qux"}))
    return p


def make_args(**kwargs) -> argparse.Namespace:
    defaults = {
        "set": None,
        "unset": None,
        "rename": None,
        "overwrite_rename": False,
        "dest": None,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_patch_set_prints_path(snap: Path, capsys):
    args = make_args(snapshot=str(snap), set=["NEW=hello"])
    cmd_patch(args)
    out = capsys.readouterr().out.strip()
    assert str(snap) in out


def test_cmd_patch_set_modifies_file(snap: Path):
    args = make_args(snapshot=str(snap), set=["NEW=hello"])
    cmd_patch(args)
    data = json.loads(snap.read_text())
    assert data["NEW"] == "hello"


def test_cmd_patch_unset_removes_key(snap: Path):
    args = make_args(snapshot=str(snap), unset=["FOO"])
    cmd_patch(args)
    data = json.loads(snap.read_text())
    assert "FOO" not in data


def test_cmd_patch_rename_renames_key(snap: Path):
    args = make_args(snapshot=str(snap), rename=["FOO:FOO2"])
    cmd_patch(args)
    data = json.loads(snap.read_text())
    assert "FOO" not in data
    assert data["FOO2"] == "bar"


def test_cmd_patch_missing_snapshot_exits_1(tmp_path: Path):
    args = make_args(snapshot=str(tmp_path / "nope.json"), set=["A=1"])
    with pytest.raises(SystemExit) as exc:
        cmd_patch(args)
    assert exc.value.code == 1


def test_cmd_patch_bad_set_format_exits_1(snap: Path):
    args = make_args(snapshot=str(snap), set=["NOEQUALS"])
    with pytest.raises(SystemExit) as exc:
        cmd_patch(args)
    assert exc.value.code == 1


def test_cmd_patch_bad_rename_format_exits_1(snap: Path):
    args = make_args(snapshot=str(snap), rename=["NOCOLON"])
    with pytest.raises(SystemExit) as exc:
        cmd_patch(args)
    assert exc.value.code == 1


def test_cmd_patch_rename_error_exits_1(snap: Path):
    args = make_args(snapshot=str(snap), rename=["MISSING:OTHER"])
    with pytest.raises(SystemExit) as exc:
        cmd_patch(args)
    assert exc.value.code == 1


def test_register_patch_commands_adds_subparser():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    register_patch_commands(sub)
    parsed = parser.parse_args(["patch", "some.json", "--set", "K=V"])
    assert parsed.set == ["K=V"]
