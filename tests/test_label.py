"""Unit tests for envpack.label."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envpack.label import add_label, list_labels, remove_label, resolve_label


@pytest.fixture()
def label_file(tmp_path: Path) -> Path:
    return tmp_path / "labels.json"


def test_add_label_returns_true_for_new(label_file):
    assert add_label("prod", "/snaps/prod.json", label_file) is True


def test_add_label_creates_file(label_file):
    add_label("prod", "/snaps/prod.json", label_file)
    assert label_file.exists()


def test_add_label_file_is_valid_json(label_file):
    add_label("prod", "/snaps/prod.json", label_file)
    data = json.loads(label_file.read_text())
    assert isinstance(data, dict)


def test_add_label_returns_false_when_updated(label_file):
    add_label("prod", "/snaps/prod.json", label_file)
    assert add_label("prod", "/snaps/prod_v2.json", label_file) is False


def test_add_label_updates_path(label_file):
    add_label("prod", "/snaps/prod.json", label_file)
    add_label("prod", "/snaps/prod_v2.json", label_file)
    assert resolve_label("prod", label_file) == "/snaps/prod_v2.json"


def test_resolve_label_returns_path(label_file):
    add_label("staging", "/snaps/staging.json", label_file)
    assert resolve_label("staging", label_file) == "/snaps/staging.json"


def test_resolve_label_missing_returns_none(label_file):
    assert resolve_label("ghost", label_file) is None


def test_remove_label_returns_true(label_file):
    add_label("dev", "/snaps/dev.json", label_file)
    assert remove_label("dev", label_file) is True


def test_remove_label_removes_entry(label_file):
    add_label("dev", "/snaps/dev.json", label_file)
    remove_label("dev", label_file)
    assert resolve_label("dev", label_file) is None


def test_remove_label_missing_returns_false(label_file):
    assert remove_label("nope", label_file) is False


def test_list_labels_empty(label_file):
    assert list_labels(label_file) == []


def test_list_labels_returns_sorted(label_file):
    add_label("z-snap", "/z.json", label_file)
    add_label("a-snap", "/a.json", label_file)
    entries = list_labels(label_file)
    assert [e["label"] for e in entries] == ["a-snap", "z-snap"]


def test_list_labels_contains_all(label_file):
    add_label("prod", "/prod.json", label_file)
    add_label("staging", "/staging.json", label_file)
    labels = {e["label"] for e in list_labels(label_file)}
    assert labels == {"prod", "staging"}
