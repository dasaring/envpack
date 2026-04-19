"""Tests for envpack.watch."""

from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

import pytest

from envpack.watch import snapshot_diff_from_baseline, changed_since, poll_for_changes


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    # Ensure a predictable environment subset for tests
    monkeypatch.setenv("WATCH_A", "1")
    monkeypatch.setenv("WATCH_B", "2")
    yield


def test_snapshot_diff_no_changes(monkeypatch):
    from envpack.snapshot import capture
    baseline = capture(keys=["WATCH_A", "WATCH_B"])
    diff = snapshot_diff_from_baseline(baseline, keys=["WATCH_A", "WATCH_B"])
    assert diff.is_empty()


def test_snapshot_diff_detects_added(monkeypatch):
    from envpack.snapshot import capture
    baseline = capture(keys=["WATCH_A", "WATCH_B"])
    monkeypatch.setenv("WATCH_C", "3")
    diff = snapshot_diff_from_baseline(baseline, keys=["WATCH_A", "WATCH_B", "WATCH_C"])
    assert "WATCH_C" in diff.added


def test_snapshot_diff_detects_removed(monkeypatch):
    from envpack.snapshot import capture
    baseline = capture(keys=["WATCH_A", "WATCH_B"])
    monkeypatch.delenv("WATCH_B")
    diff = snapshot_diff_from_baseline(baseline, keys=["WATCH_A", "WATCH_B"])
    assert "WATCH_B" in diff.removed


def test_snapshot_diff_detects_changed(monkeypatch):
    from envpack.snapshot import capture
    baseline = capture(keys=["WATCH_A"])
    monkeypatch.setenv("WATCH_A", "999")
    diff = snapshot_diff_from_baseline(baseline, keys=["WATCH_A"])
    assert "WATCH_A" in diff.changed


def test_changed_since_returns_list(monkeypatch):
    from envpack.snapshot import capture
    baseline = capture(keys=["WATCH_A", "WATCH_B"])
    monkeypatch.setenv("WATCH_A", "changed")
    result = changed_since(baseline, keys=["WATCH_A", "WATCH_B"])
    assert "WATCH_A" in result


def test_changed_since_empty_when_no_change(monkeypatch):
    from envpack.snapshot import capture
    baseline = capture(keys=["WATCH_A", "WATCH_B"])
    result = changed_since(baseline, keys=["WATCH_A", "WATCH_B"])
    assert result == []


def test_poll_calls_callback_on_change(monkeypatch):
    from envpack.snapshot import capture

    baseline_snap = capture(keys=["WATCH_A"])
    callback = MagicMock()

    call_count = 0

    original_capture = __import__("envpack.snapshot", fromlist=["capture"]).capture

    def fake_capture(keys=None):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return {"WATCH_A": "1"}
        return {"WATCH_A": "updated"}

    with patch("envpack.watch.capture", side_effect=fake_capture), \
         patch("envpack.watch.time.sleep"):
        poll_for_changes(interval=0, callback=callback, max_iterations=2)

    callback.assert_called_once()
