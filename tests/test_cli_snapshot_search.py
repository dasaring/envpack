"""Tests for envpack.cli_snapshot_search."""

from __future__ import annotations

import argparse
import json
import sys

import pytest

from envpack.cli_snapshot_search import cmd_search, register_search_commands


@pytest.fixture()
def snap_dir(tmp_path):
    data = {"vars": {"DATABASE_URL": "postgres://localhost", "SECRET_KEY": "abc"}}
    (tmp_path / "snap.json").write_text(json.dumps(data))
    return tmp_path


def make_args(**kwargs):
    defaults = {"directory": ".", "key": "", "value": ""}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_search_by_key_prints_path(snap_dir, capsys):
    args = make_args(directory=str(snap_dir), key="DATABASE_URL")
    cmd_search(args)
    out = capsys.readouterr().out
    assert "snap.json" in out
    assert "DATABASE_URL" in out


def test_cmd_search_no_results_prints_message(snap_dir, capsys):
    args = make_args(directory=str(snap_dir), key="NONEXISTENT")
    cmd_search(args)
    out = capsys.readouterr().out
    assert "No matching" in out


def test_cmd_search_no_criteria_exits_1(snap_dir):
    args = make_args(directory=str(snap_dir))
    with pytest.raises(SystemExit) as exc_info:
        cmd_search(args)
    assert exc_info.value.code == 1


def test_cmd_search_bad_directory_exits_1(tmp_path):
    args = make_args(directory=str(tmp_path / "missing"), key="FOO")
    with pytest.raises(SystemExit) as exc_info:
        cmd_search(args)
    assert exc_info.value.code == 1


def test_register_search_commands_adds_subparser():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    register_search_commands(sub)
    parsed = parser.parse_args(["search", ".", "--key", "FOO"])
    assert parsed.key == "FOO"
    assert parsed.directory == "."
