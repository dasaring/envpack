"""Tests for envpack.snapshot_graph."""

from __future__ import annotations

import json
import pytest
from pathlib import Path

from envpack.snapshot_graph import (
    build_graph,
    roots,
    leaves,
    ancestors,
    descendants,
    GraphNode,
)


@pytest.fixture
def history_file(tmp_path):
    snap_a = str(tmp_path / "a.json")
    snap_b = str(tmp_path / "b.json")
    snap_c = str(tmp_path / "c.json")

    entries = [
        {"snapshot_path": snap_a, "label": "first", "timestamp": "2024-01-01T00:00:00"},
        {"snapshot_path": snap_b, "label": None, "timestamp": "2024-01-02T00:00:00"},
        {"snapshot_path": snap_c, "label": "latest", "timestamp": "2024-01-03T00:00:00"},
    ]
    hf = tmp_path / "history.json"
    hf.write_text("\n".join(json.dumps(e) for e in entries))
    return hf, snap_a, snap_b, snap_c


def test_build_graph_returns_all_nodes(history_file):
    hf, snap_a, snap_b, snap_c = history_file
    graph = build_graph(hf)
    assert snap_a in graph
    assert snap_b in graph
    assert snap_c in graph


def test_build_graph_empty_history(tmp_path):
    hf = tmp_path / "empty.json"
    hf.write_text("")
    graph = build_graph(hf)
    assert graph == {}


def test_build_graph_parent_child_links(history_file):
    hf, snap_a, snap_b, snap_c = history_file
    graph = build_graph(hf)
    assert snap_b in graph[snap_a].children
    assert snap_a in graph[snap_b].parents
    assert snap_c in graph[snap_b].children
    assert snap_b in graph[snap_c].parents


def test_roots_returns_first_node(history_file):
    hf, snap_a, snap_b, snap_c = history_file
    graph = build_graph(hf)
    r = roots(graph)
    assert snap_a in r
    assert snap_b not in r
    assert snap_c not in r


def test_leaves_returns_last_node(history_file):
    hf, snap_a, snap_b, snap_c = history_file
    graph = build_graph(hf)
    lv = leaves(graph)
    assert snap_c in lv
    assert snap_a not in lv


def test_ancestors_of_leaf(history_file):
    hf, snap_a, snap_b, snap_c = history_file
    graph = build_graph(hf)
    anc = ancestors(graph, snap_c)
    assert snap_b in anc
    assert snap_a in anc


def test_ancestors_of_root_is_empty(history_file):
    hf, snap_a, snap_b, snap_c = history_file
    graph = build_graph(hf)
    assert ancestors(graph, snap_a) == []


def test_descendants_of_root(history_file):
    hf, snap_a, snap_b, snap_c = history_file
    graph = build_graph(hf)
    desc = descendants(graph, snap_a)
    assert snap_b in desc
    assert snap_c in desc


def test_descendants_of_leaf_is_empty(history_file):
    hf, snap_a, snap_b, snap_c = history_file
    graph = build_graph(hf)
    assert descendants(graph, snap_c) == []


def test_graph_node_to_dict():
    node = GraphNode("/tmp/snap.json", label="v1")
    node.children.append("/tmp/snap2.json")
    d = node.to_dict()
    assert d["snapshot_path"] == "/tmp/snap.json"
    assert d["label"] == "v1"
    assert "/tmp/snap2.json" in d["children"]
    assert d["parents"] == []
