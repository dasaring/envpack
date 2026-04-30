"""Unit tests for envpack.snapshot_lineage."""
import json
import pytest
from pathlib import Path

from envpack import snapshot_lineage as lin


@pytest.fixture
def store(tmp_path):
    return tmp_path / "lineage.json"


def test_set_parent_returns_true_for_new(store):
    assert lin.set_parent("snap_b.json", "snap_a.json", store=store) is True


def test_set_parent_creates_file(store):
    lin.set_parent("snap_b.json", "snap_a.json", store=store)
    assert store.exists()


def test_set_parent_file_is_valid_json(store):
    lin.set_parent("snap_b.json", "snap_a.json", store=store)
    data = json.loads(store.read_text())
    assert isinstance(data, dict)


def test_set_parent_returns_false_when_updated(store):
    lin.set_parent("snap_b.json", "snap_a.json", store=store)
    assert lin.set_parent("snap_b.json", "snap_c.json", store=store) is False


def test_get_parent_returns_correct_value(store):
    lin.set_parent("snap_b.json", "snap_a.json", store=store)
    assert lin.get_parent("snap_b.json", store=store) == "snap_a.json"


def test_get_parent_returns_none_for_missing(store):
    assert lin.get_parent("nonexistent.json", store=store) is None


def test_remove_parent_returns_true(store):
    lin.set_parent("snap_b.json", "snap_a.json", store=store)
    assert lin.remove_parent("snap_b.json", store=store) is True


def test_remove_parent_returns_false_if_not_present(store):
    assert lin.remove_parent("snap_b.json", store=store) is False


def test_remove_parent_actually_removes(store):
    lin.set_parent("snap_b.json", "snap_a.json", store=store)
    lin.remove_parent("snap_b.json", store=store)
    assert lin.get_parent("snap_b.json", store=store) is None


def test_get_children_returns_correct_list(store):
    lin.set_parent("snap_b.json", "snap_a.json", store=store)
    lin.set_parent("snap_c.json", "snap_a.json", store=store)
    children = lin.get_children("snap_a.json", store=store)
    assert set(children) == {"snap_b.json", "snap_c.json"}


def test_get_children_empty_when_none(store):
    lin.set_parent("snap_b.json", "snap_a.json", store=store)
    assert lin.get_children("snap_b.json", store=store) == []


def test_ancestors_returns_chain(store):
    lin.set_parent("snap_c.json", "snap_b.json", store=store)
    lin.set_parent("snap_b.json", "snap_a.json", store=store)
    chain = lin.ancestors("snap_c.json", store=store)
    assert chain == ["snap_b.json", "snap_a.json"]


def test_ancestors_empty_for_root(store):
    lin.set_parent("snap_b.json", "snap_a.json", store=store)
    assert lin.ancestors("snap_a.json", store=store) == []


def test_ancestors_stops_on_cycle(store):
    lin.set_parent("snap_a.json", "snap_b.json", store=store)
    lin.set_parent("snap_b.json", "snap_a.json", store=store)
    result = lin.ancestors("snap_a.json", store=store)
    assert len(result) < 10  # did not loop forever


def test_list_lineage_returns_all(store):
    lin.set_parent("snap_b.json", "snap_a.json", store=store)
    lin.set_parent("snap_c.json", "snap_b.json", store=store)
    data = lin.list_lineage(store=store)
    assert data["snap_b.json"] == "snap_a.json"
    assert data["snap_c.json"] == "snap_b.json"
