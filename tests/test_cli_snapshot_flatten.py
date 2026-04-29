"""Tests for envpack.cli_snapshot_flatten."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from envpack.cli_snapshot_flatten import (
    cmd_flatten_group,
    cmd_flatten_prefix,
    cmd_flatten_strip,
)


@pytest.fixture()
def snap(tmp_path) -> Path:
    data = {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "APP_NAME": "envpack",
        "PLAIN": "value",
    }
    p = tmp_path / "snap.json"
    p.write_text(json.dumps(data))
    return p


def make_args(**kwargs):
    defaults = {"sep": "_"}
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def test_cmd_flatten_group_creates_files(snap, tmp_path, capsys):
    out_dir = tmp_path / "groups"
    args = make_args(snapshot=str(snap), output_dir=str(out_dir))
    cmd_flatten_group(args)
    assert (out_dir / "DB.json").exists()
    assert (out_dir / "APP.json").exists()


def test_cmd_flatten_group_prints_paths(snap, tmp_path, capsys):
    out_dir = tmp_path / "groups"
    args = make_args(snapshot=str(snap), output_dir=str(out_dir))
    cmd_flatten_group(args)
    captured = capsys.readouterr().out
    assert "DB.json" in captured


def test_cmd_flatten_prefix_writes_file(snap, tmp_path, capsys):
    dest = tmp_path / "prefixed.json"
    args = make_args(snapshot=str(snap), prefix="SVC", output=str(dest))
    cmd_flatten_prefix(args)
    assert dest.exists()
    data = json.loads(dest.read_text())
    assert "SVC_DB_HOST" in data


def test_cmd_flatten_prefix_prints_path(snap, tmp_path, capsys):
    dest = tmp_path / "prefixed.json"
    args = make_args(snapshot=str(snap), prefix="SVC", output=str(dest))
    cmd_flatten_prefix(args)
    captured = capsys.readouterr().out
    assert str(dest) in captured


def test_cmd_flatten_prefix_empty_prefix_exits_1(snap, tmp_path):
    dest = tmp_path / "out.json"
    args = make_args(snapshot=str(snap), prefix="", output=str(dest))
    with pytest.raises(SystemExit) as exc:
        cmd_flatten_prefix(args)
    assert exc.value.code == 1


def test_cmd_flatten_strip_writes_file(snap, tmp_path, capsys):
    dest = tmp_path / "stripped.json"
    args = make_args(snapshot=str(snap), prefix="DB", output=str(dest))
    cmd_flatten_strip(args)
    data = json.loads(dest.read_text())
    assert "HOST" in data
    assert "PORT" in data
    assert "DB_HOST" not in data


def test_cmd_flatten_strip_drops_non_matching(snap, tmp_path):
    dest = tmp_path / "stripped.json"
    args = make_args(snapshot=str(snap), prefix="DB", output=str(dest))
    cmd_flatten_strip(args)
    data = json.loads(dest.read_text())
    assert "PLAIN" not in data
    assert "APP_NAME" not in data
