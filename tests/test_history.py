"""Tests for envpack.history module."""

from __future__ import annotations

import json
import pytest
from pathlib import Path

from envpack import history


@pytest.fixture
def history_file(tmp_path):
    return str(tmp_path / "test_history.json")


def test_record_creates_file(history_file):
    history.record_snapshot("snap_a.json", history_file=history_file)
    assert Path(history_file).exists()


def test_record_returns_dict(history_file):
    entry = history.record_snapshot("snap_a.json", label="baseline", history_file=history_file)
    assert entry["snapshot_path"] == "snap_a.json"
    assert entry["label"] == "baseline"
    assert "recorded_at" in entry


def test_record_appends(history_file):
    history.record_snapshot("snap_a.json", history_file=history_file)
    history.record_snapshot("snap_b.json", history_file=history_file)
    entries = history.list_history(history_file=history_file)
    assert len(entries) == 2


def test_list_empty(history_file):
    entries = history.list_history(history_file=history_file)
    assert entries == []


def test_find_by_label(history_file):
    history.record_snapshot("snap_a.json", label="v1", history_file=history_file)
    history.record_snapshot("snap_b.json", label="v2", history_file=history_file)
    history.record_snapshot("snap_c.json", label="v1", history_file=history_file)
    results = history.find_by_label("v1", history_file=history_file)
    assert len(results) == 2
    assert all(e["label"] == "v1" for e in results)


def test_find_by_label_no_match(history_file):
    history.record_snapshot("snap_a.json", label="v1", history_file=history_file)
    results = history.find_by_label("nonexistent", history_file=history_file)
    assert results == []


def test_remove_entry(history_file):
    history.record_snapshot("snap_a.json", history_file=history_file)
    history.record_snapshot("snap_b.json", history_file=history_file)
    removed = history.remove_entry("snap_a.json", history_file=history_file)
    assert removed is True
    entries = history.list_history(history_file=history_file)
    assert len(entries) == 1
    assert entries[0]["snapshot_path"] == "snap_b.json"


def test_remove_entry_not_found(history_file):
    history.record_snapshot("snap_a.json", history_file=history_file)
    removed = history.remove_entry("nonexistent.json", history_file=history_file)
    assert removed is False


def test_clear_history(history_file):
    history.record_snapshot("snap_a.json", history_file=history_file)
    history.clear_history(history_file=history_file)
    assert history.list_history(history_file=history_file) == []


def test_history_file_is_valid_json(history_file):
    history.record_snapshot("snap_a.json", label="test", history_file=history_file)
    with open(history_file) as f:
        data = json.load(f)
    assert isinstance(data, list)


def test_record_snapshot_recorded_at_is_iso_format(history_file):
    """Ensure recorded_at timestamp is a valid ISO 8601 string."""
    from datetime import datetime

    entry = history.record_snapshot("snap_a.json", history_file=history_file)
    # Should not raise if the format is valid ISO 8601
    parsed = datetime.fromisoformat(entry["recorded_at"])
    assert isinstance(parsed, datetime)


def test_record_snapshot_no_label_defaults_to_none(history_file):
    """When no label is provided, the entry label should be None or absent."""
    entry = history.record_snapshot("snap_a.json", history_file=history_file)
    assert entry.get("label") is None
