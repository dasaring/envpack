"""Tests for envpack.cli_rollback."""

import argparse
import json
from pathlib import Path

import pytest

from envpack.cli_rollback import cmd_rollback, register_rollback_commands
from envpack.snapshot import save


@pytest.fixture()
def setup(tmp_path):
    snap = tmp_path / "snap.json"
    save({"KEY": "value", "OTHER": "data"}, str(snap))

    hf = tmp_path / "history.json"
    entry = {"path": str(snap), "label": "release-1", "timestamp": "2024-06-01T12:00:00"}
    hf.write_text(json.dumps(entry) + "\n")

    dest = tmp_path / "current.json"
    return {"snap": snap, "history": hf, "dest": dest, "tmp": tmp_path}


def make_args(**kwargs):
    defaults = {"label": None, "index": -1, "dry_run": False}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_rollback_writes_dest(setup, capsys):
    args = make_args(
        dest=str(setup["dest"]),
        history_file=str(setup["history"]),
    )
    cmd_rollback(args)
    assert setup["dest"].exists()


def test_cmd_rollback_prints_path(setup, capsys):
    args = make_args(
        dest=str(setup["dest"]),
        history_file=str(setup["history"]),
    )
    cmd_rollback(args)
    out = capsys.readouterr().out
    assert str(setup["snap"]) in out


def test_cmd_rollback_dry_run(setup, capsys):
    args = make_args(
        dest=str(setup["dest"]),
        history_file=str(setup["history"]),
        dry_run=True,
    )
    cmd_rollback(args)
    assert not setup["dest"].exists()
    out = capsys.readouterr().out
    assert "dry-run" in out


def test_cmd_rollback_by_label(setup, capsys):
    args = make_args(
        dest=str(setup["dest"]),
        history_file=str(setup["history"]),
        label="release-1",
    )
    cmd_rollback(args)
    out = capsys.readouterr().out
    assert "release-1" in out


def test_cmd_rollback_empty_history_exits_1(tmp_path):
    empty_h = tmp_path / "empty.json"
    empty_h.write_text("")
    args = make_args(dest=str(tmp_path / "out.json"), history_file=str(empty_h))
    with pytest.raises(SystemExit) as exc:
        cmd_rollback(args)
    assert exc.value.code == 1


def test_register_rollback_commands():
    parser = argparse.ArgumentParser()
    subs = parser.add_subparsers()
    register_rollback_commands(subs)
    args = parser.parse_args(["rollback", "out.json", "--dry-run"])
    assert args.dry_run is True
    assert args.dest == "out.json"
