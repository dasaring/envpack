"""Tests for envpack.snapshot_expire."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from envpack.snapshot_expire import (
    get_expiry,
    is_expired,
    list_all,
    list_expired,
    remove_expiry,
    set_expiry,
)


@pytest.fixture
def store(tmp_path: Path) -> Path:
    return tmp_path / "expiry.json"


def _future() -> str:
    return (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()


def _past() -> str:
    return (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()


def test_set_expiry_returns_true_for_new(store):
    assert set_expiry("snap_a.json", _future(), store) is True


def test_set_expiry_returns_false_when_updated(store):
    set_expiry("snap_a.json", _future(), store)
    assert set_expiry("snap_a.json", _future(), store) is False


def test_set_expiry_creates_file(store):
    set_expiry("snap_a.json", _future(), store)
    assert store.exists()


def test_set_expiry_file_is_valid_json(store):
    set_expiry("snap_a.json", _future(), store)
    data = json.loads(store.read_text())
    assert "snap_a.json" in data


def test_get_expiry_returns_none_when_absent(store):
    assert get_expiry("missing.json", store) is None


def test_get_expiry_returns_set_value(store):
    expiry = _future()
    set_expiry("snap_a.json", expiry, store)
    assert get_expiry("snap_a.json", store) == expiry


def test_is_expired_false_for_future(store):
    set_expiry("snap_a.json", _future(), store)
    assert is_expired("snap_a.json", store) is False


def test_is_expired_true_for_past(store):
    set_expiry("snap_a.json", _past(), store)
    assert is_expired("snap_a.json", store) is True


def test_is_expired_false_when_no_expiry(store):
    assert is_expired("snap_a.json", store) is False


def test_remove_expiry_returns_true_when_present(store):
    set_expiry("snap_a.json", _future(), store)
    assert remove_expiry("snap_a.json", store) is True


def test_remove_expiry_returns_false_when_absent(store):
    assert remove_expiry("snap_a.json", store) is False


def test_remove_expiry_actually_removes(store):
    set_expiry("snap_a.json", _future(), store)
    remove_expiry("snap_a.json", store)
    assert get_expiry("snap_a.json", store) is None


def test_list_expired_returns_only_past(store):
    set_expiry("old.json", _past(), store)
    set_expiry("new.json", _future(), store)
    expired = list_expired(store)
    assert "old.json" in expired
    assert "new.json" not in expired


def test_list_expired_empty_when_none_expired(store):
    set_expiry("snap_a.json", _future(), store)
    assert list_expired(store) == []


def test_list_all_returns_all_entries(store):
    set_expiry("snap_a.json", _future(), store)
    set_expiry("snap_b.json", _past(), store)
    all_entries = list_all(store)
    assert len(all_entries) == 2
    assert "snap_a.json" in all_entries
    assert "snap_b.json" in all_entries
