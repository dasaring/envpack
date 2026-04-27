"""Tests for envpack.cli_snapshot_score."""
import json
import argparse
import pytest
from pathlib import Path

from envpack.cli_snapshot_score import cmd_score, register_score_commands


@pytest.fixture
def snap(tmp_path):
    p = tmp_path / "snap.json"
    p.write_text(json.dumps({"APP_ENV": "production", "LOG_LEVEL": "debug"}))
    return p


def make_args(**kwargs):
    defaults = {"require": None, "min_score": None}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_score_prints_summary(snap, capsys):
    cmd_score(make_args(snapshot=str(snap)))
    out = capsys.readouterr().out
    assert "Score:" in out


def test_cmd_score_shows_breakdown(snap, capsys):
    cmd_score(make_args(snapshot=str(snap)))
    out = capsys.readouterr().out
    assert "non_empty" in out


def test_cmd_score_missing_file_exits_1(tmp_path):
    with pytest.raises(SystemExit) as exc:
        cmd_score(make_args(snapshot=str(tmp_path / "nope.json")))
    assert exc.value.code == 1


def test_cmd_score_min_score_pass(snap):
    # Should not raise; score will be high for a clean snap
    cmd_score(make_args(snapshot=str(snap), min_score=0.0))


def test_cmd_score_min_score_fail(snap):
    with pytest.raises(SystemExit) as exc:
        cmd_score(make_args(snapshot=str(snap), min_score=999.0))
    assert exc.value.code == 1


def test_cmd_score_with_required_keys_present(snap, capsys):
    cmd_score(make_args(snapshot=str(snap), require="APP_ENV,LOG_LEVEL"))
    out = capsys.readouterr().out
    assert "Score:" in out


def test_cmd_score_with_required_keys_missing(snap, capsys):
    cmd_score(make_args(snapshot=str(snap), require="MISSING_KEY"))
    out = capsys.readouterr().out
    assert "Missing" in out


def test_register_score_commands_adds_subparser():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    register_score_commands(sub)
    args = parser.parse_args(["score", "somefile.json"])
    assert args.snapshot == "somefile.json"
