"""Unit tests for envpack.cli_label."""

from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from envpack.cli_label import (
    cmd_label_add,
    cmd_label_list,
    cmd_label_remove,
    cmd_label_resolve,
)
from envpack.label import add_label


@pytest.fixture()
def label_file(tmp_path: Path) -> Path:
    return tmp_path / "labels.json"


def make_args(label_file: Path, **kwargs) -> argparse.Namespace:
    defaults = {"store": str(label_file)}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_label_add_prints_created(label_file, capsys):
    args = make_args(label_file, label="prod", path="/snaps/prod.json")
    cmd_label_add(args)
    out = capsys.readouterr().out
    assert "Created" in out
    assert "prod" in out


def test_cmd_label_add_prints_updated(label_file, capsys):
    add_label("prod", "/old.json", label_file)
    args = make_args(label_file, label="prod", path="/new.json")
    cmd_label_add(args)
    out = capsys.readouterr().out
    assert "Updated" in out


def test_cmd_label_remove_success(label_file, capsys):
    add_label("dev", "/dev.json", label_file)
    args = make_args(label_file, label="dev")
    cmd_label_remove(args)
    out = capsys.readouterr().out
    assert "Removed" in out


def test_cmd_label_remove_missing_exits_1(label_file):
    args = make_args(label_file, label="ghost")
    with pytest.raises(SystemExit) as exc:
        cmd_label_remove(args)
    assert exc.value.code == 1


def test_cmd_label_resolve_prints_path(label_file, capsys):
    add_label("staging", "/staging.json", label_file)
    args = make_args(label_file, label="staging")
    cmd_label_resolve(args)
    out = capsys.readouterr().out.strip()
    assert out == "/staging.json"


def test_cmd_label_resolve_missing_exits_1(label_file):
    args = make_args(label_file, label="nope")
    with pytest.raises(SystemExit) as exc:
        cmd_label_resolve(args)
    assert exc.value.code == 1


def test_cmd_label_list_empty(label_file, capsys):
    args = make_args(label_file)
    cmd_label_list(args)
    out = capsys.readouterr().out
    assert "No labels" in out


def test_cmd_label_list_shows_entries(label_file, capsys):
    add_label("prod", "/prod.json", label_file)
    add_label("dev", "/dev.json", label_file)
    args = make_args(label_file)
    cmd_label_list(args)
    out = capsys.readouterr().out
    assert "prod" in out
    assert "dev" in out
