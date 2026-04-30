"""Integration tests for snapshot lineage: verifies lineage against real snapshot files."""
import json
import pytest
from pathlib import Path

from envpack import snapshot_lineage as lin


@pytest.fixture
def snapshot_path(tmp_path):
    def _make(name: str, data: dict) -> str:
        p = tmp_path / name
        p.write_text(json.dumps(data))
        return str(p)
    return _make


@pytest.fixture
def store(tmp_path):
    return tmp_path / "lineage.json"


def test_lineage_references_existing_snapshot(snapshot_path, store):
    a = snapshot_path("snap_a.json", {"APP": "v1"})
    b = snapshot_path("snap_b.json", {"APP": "v2"})
    lin.set_parent(b, a, store=store)
    assert lin.get_parent(b, store=store) == a
    assert Path(a).exists()


def test_lineage_lifecycle(snapshot_path, store):
    a = snapshot_path("snap_a.json", {"K": "1"})
    b = snapshot_path("snap_b.json", {"K": "2"})
    c = snapshot_path("snap_c.json", {"K": "3"})
    lin.set_parent(b, a, store=store)
    lin.set_parent(c, b, store=store)

    assert lin.ancestors(c, store=store) == [b, a]
    assert set(lin.get_children(a, store=store)) == {b}

    lin.remove_parent(b, store=store)
    assert lin.ancestors(c, store=store) == []  # chain broken


def test_multiple_children_tracked_independently(snapshot_path, store):
    root = snapshot_path("root.json", {"BASE": "1"})
    child1 = snapshot_path("child1.json", {"BASE": "2"})
    child2 = snapshot_path("child2.json", {"BASE": "3"})
    lin.set_parent(child1, root, store=store)
    lin.set_parent(child2, root, store=store)

    children = lin.get_children(root, store=store)
    assert child1 in children
    assert child2 in children
    assert len(children) == 2


def test_full_lineage_list_reflects_all_entries(snapshot_path, store):
    a = snapshot_path("a.json", {})
    b = snapshot_path("b.json", {})
    c = snapshot_path("c.json", {})
    lin.set_parent(b, a, store=store)
    lin.set_parent(c, b, store=store)
    data = lin.list_lineage(store=store)
    assert len(data) == 2
    assert data[b] == a
    assert data[c] == b
