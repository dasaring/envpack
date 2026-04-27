"""Tests for envpack.cli_snapshot_sort."""
from __future__ import annotations

import argparse
import json
import sys
import pytest

from envpack.cli_snapshot_sort import cmd_sort, register_sort_commands


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def make_args(**kwargs):
    defaults = {"path": "", "strategy": "alpha", "keys": None}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


@pytest.fixture()
def snap(tmp_path):
    p = tmp_path / "env.json"
    p.write_text(json.dumps({"Z": "26", "A": "1", "M": "13"}))
    return p


# ---------------------------------------------------------------------------
# cmd_sort
# ---------------------------------------------------------------------------

def test_cmd_sort_prints_sorted_path(snap, capsys):
    args = make_args(path=str(snap))
    cmd_sort(args)
    out = capsys.readouterr().out
    assert "Sorted:" in out
    assert str(snap) in out


def test_cmd_sort_modifies_file(snap):
    args = make_args(path=str(snap))
    cmd_sort(args)
    loaded = json.loads(snap.read_text())
    assert list(loaded.keys()) == ["A", "M", "Z"]


def test_cmd_sort_with_strategy(snap):
    args = make_args(path=str(snap), strategy="alpha_desc")
    cmd_sort(args)
    loaded = json.loads(snap.read_text())
    assert list(loaded.keys()) == ["Z", "M", "A"]


def test_cmd_sort_missing_file_exits_1(tmp_path, capsys):
    args = make_args(path=str(tmp_path / "missing.json"))
    with pytest.raises(SystemExit) as exc_info:
        cmd_sort(args)
    assert exc_info.value.code == 1
    assert "not found" in capsys.readouterr().err


def test_cmd_sort_invalid_strategy_exits_1(snap, capsys):
    args = make_args(path=str(snap), strategy="bogus")
    with pytest.raises(SystemExit) as exc_info:
        cmd_sort(args)
    assert exc_info.value.code == 1
    assert "Error" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# register_sort_commands
# ---------------------------------------------------------------------------

def test_register_sort_commands_adds_sort_subcommand():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    register_sort_commands(sub)
    args = parser.parse_args(["sort", "some/path.json"])
    assert args.path == "some/path.json"
    assert args.strategy == "alpha"
    assert args.func is cmd_sort
