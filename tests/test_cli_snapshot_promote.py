"""Tests for envpack.cli_snapshot_promote."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from envpack.cli_snapshot_promote import cmd_promote


@pytest.fixture()
def snap(tmp_path) -> Path:
    p = tmp_path / "dev.json"
    p.write_text(json.dumps({"APP_ENV": "dev", "SECRET": "abc", "PORT": "8080"}))
    return p


def make_args(**kwargs):
    defaults = dict(source=None, dest=None, overwrite=False, strip=None, add=None, dry_run=False)
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def test_cmd_promote_prints_path(snap, tmp_path, capsys):
    dest = tmp_path / "staging.json"
    cmd_promote(make_args(source=str(snap), dest=str(dest)))
    out = capsys.readouterr().out
    assert str(dest) in out


def test_cmd_promote_creates_file(snap, tmp_path):
    dest = tmp_path / "staging.json"
    cmd_promote(make_args(source=str(snap), dest=str(dest)))
    assert dest.exists()


def test_cmd_promote_strip_removes_key(snap, tmp_path):
    dest = tmp_path / "staging.json"
    cmd_promote(make_args(source=str(snap), dest=str(dest), strip=["SECRET"]))
    data = json.loads(dest.read_text())
    assert "SECRET" not in data


def test_cmd_promote_add_injects_key(snap, tmp_path):
    dest = tmp_path / "staging.json"
    cmd_promote(make_args(source=str(snap), dest=str(dest), add=["STAGE=staging"]))
    data = json.loads(dest.read_text())
    assert data["STAGE"] == "staging"


def test_cmd_promote_missing_source_exits_1(tmp_path):
    dest = tmp_path / "dest.json"
    with pytest.raises(SystemExit) as exc:
        cmd_promote(make_args(source=str(tmp_path / "nope.json"), dest=str(dest)))
    assert exc.value.code == 1


def test_cmd_promote_no_overwrite_exits_1(snap, tmp_path, capsys):
    dest = tmp_path / "dest.json"
    dest.write_text(json.dumps({"X": "1"}))
    with pytest.raises(SystemExit) as exc:
        cmd_promote(make_args(source=str(snap), dest=str(dest)))
    assert exc.value.code == 1


def test_cmd_promote_dry_run_no_file_created(snap, tmp_path, capsys):
    dest = tmp_path / "staging.json"
    cmd_promote(make_args(source=str(snap), dest=str(dest), dry_run=True))
    assert not dest.exists()
    out = capsys.readouterr().out
    assert "Dry-run" in out


def test_cmd_promote_bad_add_format_exits_1(snap, tmp_path, capsys):
    dest = tmp_path / "dest.json"
    with pytest.raises(SystemExit) as exc:
        cmd_promote(make_args(source=str(snap), dest=str(dest), add=["BADVALUE"]))
    assert exc.value.code == 1
    err = capsys.readouterr().err
    assert "KEY=VALUE" in err
