"""Tests for envpack.tags module."""

import pytest
from pathlib import Path
from envpack.tags import (
    add_tag, remove_tag, get_snapshots_by_tag,
    get_tags_for_snapshot, list_all_tags,
)


@pytest.fixture
def tags_file(tmp_path):
    return tmp_path / "tags.json"


def test_add_tag_creates_entry(tags_file):
    add_tag("/tmp/snap.json", "production", tags_file)
    result = get_snapshots_by_tag("production", tags_file)
    assert "/tmp/snap.json" in result


def test_add_tag_no_duplicates(tags_file):
    add_tag("/tmp/snap.json", "staging", tags_file)
    add_tag("/tmp/snap.json", "staging", tags_file)
    result = get_snapshots_by_tag("staging", tags_file)
    assert result.count("/tmp/snap.json") == 1


def test_add_multiple_snapshots_to_tag(tags_file):
    add_tag("/tmp/a.json", "dev", tags_file)
    add_tag("/tmp/b.json", "dev", tags_file)
    result = get_snapshots_by_tag("dev", tags_file)
    assert "/tmp/a.json" in result
    assert "/tmp/b.json" in result


def test_remove_tag_returns_true(tags_file):
    add_tag("/tmp/snap.json", "old", tags_file)
     = remove_tag("/tmp/snap.json", "old", tags_file)
    assert removed is True


def test_remove_tag_cleans_empty_tag(tags_file):
    add_tag("/tmp/snap.json", "temp", tags_file)
    remove_tag("/tmp/snap.json", "temp", tags_file)
    assert "temp" not in list_all_tags(tags_file)


def test_remove_tag_not_found_returns_false(tags_file):
    result = remove_tag("/tmp/nonexistent.json", "ghost", tags_file)
    assert result is False


def test_get_tags_for_snapshot(tags_file):
    add_tag("/tmp/snap.json", "prod", tags_file)
    add_tag("/tmp/snap.json", "v2", tags_file)
    tags = get_tags_for_snapshot("/tmp/snap.json", tags_file)
    assert "prod" in tags
    assert "v2" in tags


def test_get_snapshots_by_missing_tag_returns_empty(tags_file):
    result = get_snapshots_by_tag("nonexistent", tags_file)
    assert result == []


def test_list_all_tags_empty(tags_file):
    result = list_all_tags(tags_file)
    assert result == {}


def test_list_all_tags_populated(tags_file):
    add_tag("/tmp/x.json", "alpha", tags_file)
    add_tag("/tmp/y.json", "beta", tags_file)
    result = list_all_tags(tags_file)
    assert "alpha" in result
    assert "beta" in result
