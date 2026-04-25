"""Tests for envpack.snapshot_annotate."""

from __future__ import annotations

import json
import pytest
from pathlib import Path

from envpack.snapshot_annotate import (
    annotate,
    remove_annotation,
    get_annotations,
    find_by_annotation,
    clear_annotations,
)


@pytest.fixture
def store(tmp_path) -> Path:
    return tmp_path / "annotations.json"


def test_annotate_returns_true_for_new(store):
    assert annotate("snap.json", "env", "production", store=store) is True


def test_annotate_returns_false_when_updated(store):
    annotate("snap.json", "env", "production", store=store)
    assert annotate("snap.json", "env", "staging", store=store) is False


def test_annotate_creates_file(store):
    annotate("snap.json", "env", "production", store=store)
    assert store.exists()


def test_annotate_file_is_valid_json(store):
    annotate("snap.json", "env", "production", store=store)
    data = json.loads(store.read_text())
    assert isinstance(data, dict)


def test_annotate_stores_value(store):
    annotate("snap.json", "env", "production", store=store)
    data = json.loads(store.read_text())
    assert data["snap.json"]["env"] == "production"


def test_annotate_multiple_keys(store):
    annotate("snap.json", "env", "prod", store=store)
    annotate("snap.json", "owner", "alice", store=store)
    ann = get_annotations("snap.json", store=store)
    assert ann == {"env": "prod", "owner": "alice"}


def test_get_annotations_empty_for_unknown(store):
    assert get_annotations("missing.json", store=store) == {}


def test_remove_annotation_returns_true(store):
    annotate("snap.json", "env", "prod", store=store)
    assert remove_annotation("snap.json", "env", store=store) is True


def test_remove_annotation_returns_false_for_missing(store):
    assert remove_annotation("snap.json", "env", store=store) is False


def test_remove_annotation_deletes_key(store):
    annotate("snap.json", "env", "prod", store=store)
    annotate("snap.json", "owner", "alice", store=store)
    remove_annotation("snap.json", "env", store=store)
    ann = get_annotations("snap.json", store=store)
    assert "env" not in ann
    assert "owner" in ann


def test_remove_last_annotation_removes_snapshot_entry(store):
    annotate("snap.json", "env", "prod", store=store)
    remove_annotation("snap.json", "env", store=store)
    data = json.loads(store.read_text())
    assert "snap.json" not in data


def test_find_by_annotation_key_only(store):
    annotate("a.json", "env", "prod", store=store)
    annotate("b.json", "env", "staging", store=store)
    annotate("c.json", "owner", "alice", store=store)
    results = find_by_annotation("env", store=store)
    assert set(results.keys()) == {"a.json", "b.json"}


def test_find_by_annotation_key_and_value(store):
    annotate("a.json", "env", "prod", store=store)
    annotate("b.json", "env", "staging", store=store)
    results = find_by_annotation("env", "prod", store=store)
    assert list(results.keys()) == ["a.json"]


def test_find_by_annotation_no_match_returns_empty(store):
    assert find_by_annotation("env", store=store) == {}


def test_clear_annotations_returns_count(store):
    annotate("snap.json", "env", "prod", store=store)
    annotate("snap.json", "owner", "alice", store=store)
    assert clear_annotations("snap.json", store=store) == 2


def test_clear_annotations_removes_all(store):
    annotate("snap.json", "env", "prod", store=store)
    clear_annotations("snap.json", store=store)
    assert get_annotations("snap.json", store=store) == {}


def test_clear_annotations_unknown_snapshot_returns_zero(store):
    assert clear_annotations("ghost.json", store=store) == 0
