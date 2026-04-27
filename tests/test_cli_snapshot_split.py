"""Tests for envpack.cli_snapshot_split."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pytest

from envpack.cli_snapshot_split import cmd_split, register_split_commands
from envpack.snapshot import save


SAMPLE = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "AWS_KEY": "abc",
    "APP_NAME": "envpack",
}


@pytest.fixture()
def snap(tmp_path):
    p = tmp_path / "env.json"
    save(SAMPLE, p)
    return p


def make_args(**kwargs):
    defaults = dict(
        snapshot="",
        output_dir="",
        base_name="",
        prefixes="",
        groups="",
        strip_prefix=False,
        keep_empty=False,
    )
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_split_by_prefix_prints_groups(snap, tmp_path, capsys):
    out_dir = tmp_path / "out"
    args = make_args(snapshot=str(snap), output_dir=str(out_dir), prefixes="DB_,AWS_")
    cmd_split(args)
    captured = capsys.readouterr().out
    assert "DB_" in captured
    assert "AWS_" in captured


def test_cmd_split_creates_files(snap, tmp_path):
    out_dir = tmp_path / "out"
    args = make_args(snapshot=str(snap), output_dir=str(out_dir), prefixes="DB_")
    cmd_split(args)
    files = list(out_dir.glob("*.json"))
    assert len(files) >= 1


def test_cmd_split_by_groups(snap, tmp_path, capsys):
    out_dir = tmp_path / "out"
    args = make_args(
        snapshot=str(snap),
        output_dir=str(out_dir),
        groups="db:DB_HOST,DB_PORT;cloud:AWS_KEY",
    )
    cmd_split(args)
    captured = capsys.readouterr().out
    assert "db" in captured
    assert "cloud" in captured


def test_cmd_split_missing_snapshot_exits_1(tmp_path, capsys):
    out_dir = tmp_path / "out"
    args = make_args(snapshot=str(tmp_path / "nope.json"), output_dir=str(out_dir), prefixes="DB_")
    with pytest.raises(SystemExit) as exc:
        cmd_split(args)
    assert exc.value.code == 1


def test_cmd_split_no_criteria_exits_1(snap, tmp_path):
    out_dir = tmp_path / "out"
    args = make_args(snapshot=str(snap), output_dir=str(out_dir))
    with pytest.raises(SystemExit) as exc:
        cmd_split(args)
    assert exc.value.code == 1


def test_cmd_split_invalid_group_spec_exits_1(snap, tmp_path):
    out_dir = tmp_path / "out"
    args = make_args(snapshot=str(snap), output_dir=str(out_dir), groups="badspec")
    with pytest.raises(SystemExit) as exc:
        cmd_split(args)
    assert exc.value.code == 1


def test_register_split_commands_adds_subparser():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    register_split_commands(sub)
    args = parser.parse_args(["split", "snap.json", "out/", "--prefixes", "DB_"])
    assert args.prefixes == "DB_"
