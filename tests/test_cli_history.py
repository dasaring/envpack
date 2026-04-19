"""Tests for envpack.cli_history CLI commands."""

from __future__ import annotations

import argparse
import pytest

from envpack import history
from envpack import cli_history


@pytest.fixture
def history_file(tmp_path):
    return str(tmp_path / "cli_history.json")


def make_args(history_file, **kwargs):
    ns = argparse.Namespace(history_file=history_file)
    for k, v in kwargs.items():
        setattr(ns, k, v)
    return ns


def test_cmd_record_prints_path(history_file, capsys):
    args = make_args(history_file, snapshot="snap.json", label=None)
    cli_history.cmd_history_record(args)
    out = capsys.readouterr().out
    assert "snap.json" in out


def test_cmd_record_with_label(history_file, capsys):
    args = make_args(history_file, snapshot="snap.json", label="prod")
    cli_history.cmd_history_record(args)
    out = capsys.readouterr().out
    assert "[prod]" in out


def test_cmd_list_empty(history_file, capsys):
    args = make_args(history_file)
    cli_history.cmd_history_list(args)
    out = capsys.readouterr().out
    assert "No history" in out


def test_cmd_list_shows_entries(history_file, capsys):
    history.record_snapshot("snap_a.json", label="v1", history_file=history_file)
    args = make_args(history_file)
    cli_history.cmd_history_list(args)
    out = capsys.readouterr().out
    assert "snap_a.json" in out
    assert "[v1]" in out


def test_cmd_find_match(history_file, capsys):
    history.record_snapshot("snap_a.json", label="dev", history_file=history_file)
    args = make_args(history_file, label="dev")
    cli_history.cmd_history_find(args)
    out = capsys.readouterr().out
    assert "snap_a.json" in out


def test_cmd_find_no_match(history_file, capsys):
    args = make_args(history_file, label="missing")
    cli_history.cmd_history_find(args)
    out = capsys.readouterr().out
    assert "No entries" in out


def test_cmd_remove_success(history_file, capsys):
    history.record_snapshot("snap_a.json", history_file=history_file)
    args = make_args(history_file, snapshot="snap_a.json")
    cli_history.cmd_history_remove(args)
    out = capsys.readouterr().out
    assert "Removed" in out


def test_cmd_remove_not_found(history_file, capsys):
    args = make_args(history_file, snapshot="ghost.json")
    cli_history.cmd_history_remove(args)
    out = capsys.readouterr().out
    assert "No entry" in out
