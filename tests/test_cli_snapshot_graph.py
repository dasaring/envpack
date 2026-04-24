"""Tests for envpack.cli_snapshot_graph."""

from __future__ import annotations

import argparse
import json
import pytest
from pathlib import Path

from envpack.cli_snapshot_graph import (
    cmd_graph_roots,
    cmd_graph_leaves,
    cmd_graph_ancestors,
    cmd_graph_descendants,
)


@pytest.fixture
def history_file(tmp_path):
    snap_a = str(tmp_path / "a.json")
    snap_b = str(tmp_path / "b.json")
    snap_c = str(tmp_path / "c.json")
    entries = [
        {"snapshot_path": snap_a, "label": "alpha", "timestamp": "2024-01-01T00:00:00"},
        {"snapshot_path": snap_b, "label": None, "timestamp": "2024-01-02T00:00:00"},
        {"snapshot_path": snap_c, "label": "gamma", "timestamp": "2024-01-03T00:00:00"},
    ]
    hf = tmp_path / "history.json"
    hf.write_text("\n".join(json.dumps(e) for e in entries))
    return hf, snap_a, snap_b, snap_c


def make_args(**kwargs) -> argparse.Namespace:
    return argparse.Namespace(**kwargs)


def test_cmd_graph_roots_prints_root(history_file, capsys):
    hf, snap_a, snap_b, snap_c = history_file
    cmd_graph_roots(make_args(history_file=str(hf)))
    out = capsys.readouterr().out
    assert snap_a in out
    assert snap_b not in out


def test_cmd_graph_roots_shows_label(history_file, capsys):
    hf, snap_a, snap_b, snap_c = history_file
    cmd_graph_roots(make_args(history_file=str(hf)))
    out = capsys.readouterr().out
    assert "alpha" in out


def test_cmd_graph_leaves_prints_leaf(history_file, capsys):
    hf, snap_a, snap_b, snap_c = history_file
    cmd_graph_leaves(make_args(history_file=str(hf)))
    out = capsys.readouterr().out
    assert snap_c in out
    assert snap_a not in out


def test_cmd_graph_ancestors_of_leaf(history_file, capsys):
    hf, snap_a, snap_b, snap_c = history_file
    cmd_graph_ancestors(make_args(history_file=str(hf), snapshot=snap_c))
    out = capsys.readouterr().out
    assert snap_b in out
    assert snap_a in out


def test_cmd_graph_ancestors_of_root_prints_none(history_file, capsys):
    hf, snap_a, snap_b, snap_c = history_file
    cmd_graph_ancestors(make_args(history_file=str(hf), snapshot=snap_a))
    out = capsys.readouterr().out
    assert "No ancestors" in out


def test_cmd_graph_descendants_of_root(history_file, capsys):
    hf, snap_a, snap_b, snap_c = history_file
    cmd_graph_descendants(make_args(history_file=str(hf), snapshot=snap_a))
    out = capsys.readouterr().out
    assert snap_b in out
    assert snap_c in out


def test_cmd_graph_descendants_of_leaf_prints_none(history_file, capsys):
    hf, snap_a, snap_b, snap_c = history_file
    cmd_graph_descendants(make_args(history_file=str(hf), snapshot=snap_c))
    out = capsys.readouterr().out
    assert "No descendants" in out
