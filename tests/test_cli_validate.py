"""Tests for envpack.cli_validate."""
import json
import pytest
from pathlib import Path
from unittest.mock import patch
from envpack.cli_validate import cmd_validate


@pytest.fixture
def snap_file(tmp_path):
    data = {"HOME": "/home/user", "USER": "alice"}
    p = tmp_path / "snap.json"
    p.write_text(json.dumps(data))
    return str(p)


def make_args(file, require=None, forbid=None, max_value_length=4096):
    class A:
        pass
    a = A()
    a.file = file
    a.require = require
    a.forbid = forbid
    a.max_value_length = max_value_length
    return a


def test_valid_snapshot_exits_0(snap_file, capsys):
    cmd_validate(make_args(snap_file))
    out = capsys.readouterr().out
    assert "valid" in out.lower()


def test_missing_required_key_exits_1(snap_file):
    with pytest.raises(SystemExit) as exc:
        cmd_validate(make_args(snap_file, require=["MISSING_KEY"]))
    assert exc.value.code == 1


def test_forbidden_key_exits_1(snap_file):
    with pytest.raises(SystemExit) as exc:
        cmd_validate(make_args(snap_file, forbid=["HOME"]))
    assert exc.value.code == 1


def test_all_required_present_exits_0(snap_file, capsys):
    cmd_validate(make_args(snap_file, require=["HOME", "USER"]))
    out = capsys.readouterr().out
    assert "valid" in out.lower()


def test_summary_printed(snap_file, capsys):
    cmd_validate(make_args(snap_file))
    captured = capsys.readouterr()
    assert len(captured.out) > 0


def test_value_exceeding_max_length_exits_1(tmp_path):
    """A snapshot with a value longer than max_value_length should fail validation."""
    data = {"HOME": "/home/user", "LONG_VAR": "x" * 10}
    p = tmp_path / "snap.json"
    p.write_text(json.dumps(data))
    with pytest.raises(SystemExit) as exc:
        cmd_validate(make_args(str(p), max_value_length=5))
    assert exc.value.code == 1
