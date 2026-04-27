"""Tests for envpack.cli_snapshot_mask."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pytest

from envpack.cli_snapshot_mask import cmd_mask, register_mask_commands
from envpack.snapshot_mask import DEFAULT_MASK


@pytest.fixture()
def snap(tmp_path: Path) -> Path:
    data = {"SECRET": "hunter2", "TOKEN": "abc", "HOST": "localhost"}
    p = tmp_path / "env.json"
    p.write_text(json.dumps(data))
    return p


def make_args(**kwargs) -> argparse.Namespace:
    defaults = {
        "snapshot": None,
        "keys": [],
        "pattern": None,
        "mask": DEFAULT_MASK,
        "output": None,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_mask_prints_path(snap, capsys):
    args = make_args(snapshot=snap, keys=["SECRET"])
    cmd_mask(args)
    out = capsys.readouterr().out.strip()
    assert out == str(snap)


def test_cmd_mask_modifies_file(snap):
    args = make_args(snapshot=snap, keys=["SECRET", "TOKEN"])
    cmd_mask(args)
    data = json.loads(snap.read_text())
    assert data["SECRET"] == DEFAULT_MASK
    assert data["TOKEN"] == DEFAULT_MASK
    assert data["HOST"] == "localhost"


def test_cmd_mask_with_pattern(snap):
    args = make_args(snapshot=snap, pattern=r"(SECRET|TOKEN)")
    cmd_mask(args)
    data = json.loads(snap.read_text())
    assert data["SECRET"] == DEFAULT_MASK
    assert data["TOKEN"] == DEFAULT_MASK


def test_cmd_mask_no_criteria_exits_1(snap, capsys):
    args = make_args(snapshot=snap)
    with pytest.raises(SystemExit) as exc:
        cmd_mask(args)
    assert exc.value.code == 1
    assert "pattern" in capsys.readouterr().err


def test_cmd_mask_missing_snapshot_exits_1(tmp_path, capsys):
    args = make_args(snapshot=tmp_path / "missing.json", keys=["X"])
    with pytest.raises(SystemExit) as exc:
        cmd_mask(args)
    assert exc.value.code == 1


def test_cmd_mask_output_path(snap, tmp_path):
    out = tmp_path / "out.json"
    args = make_args(snapshot=snap, keys=["SECRET"], output=out)
    cmd_mask(args)
    data = json.loads(out.read_text())
    assert data["SECRET"] == DEFAULT_MASK
    # original untouched
    original = json.loads(snap.read_text())
    assert original["SECRET"] == "hunter2"


def test_register_mask_commands_adds_subparser():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    register_mask_commands(sub)
    args = parser.parse_args(["mask", "snap.json", "--keys", "FOO"])
    assert args.func is cmd_mask
    assert args.keys == ["FOO"]
