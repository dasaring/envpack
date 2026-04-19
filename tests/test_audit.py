"""Tests for envpack.audit module."""

import json
from pathlib import Path

import pytest

from envpack.audit import log_event, read_events, clear_log


@pytest.fixture
def audit_log(tmp_path):
    return tmp_path / "test_audit.log"


def test_log_event_returns_dict(audit_log):
    event = log_event("capture", path="env.json", keys_count=5, log_file=audit_log)
    assert isinstance(event, dict)
    assert event["action"] == "capture"
    assert event["path"] == "env.json"
    assert event["keys_count"] == 5
    assert "timestamp" in event


def test_log_event_creates_file(audit_log):
    assert not audit_log.exists()
    log_event("capture", log_file=audit_log)
    assert audit_log.exists()


def test_log_event_appends(audit_log):
    log_event("capture", log_file=audit_log)
    log_event("restore", log_file=audit_log)
    events = read_events(audit_log)
    assert len(events) == 2
    assert events[0]["action"] == "capture"
    assert events[1]["action"] == "restore"


def test_log_event_valid_json_lines(audit_log):
    log_event("diff", path="a.json", log_file=audit_log)
    lines = audit_log.read_text().strip().splitlines()
    assert len(lines) == 1
    parsed = json.loads(lines[0])
    assert parsed["action"] == "diff"


def test_log_event_extra_fields(audit_log):
    event = log_event("restore", extra={"shell": "bash"}, log_file=audit_log)
    assert event["shell"] == "bash"


def test_read_events_empty_when_no_file(audit_log):
    events = read_events(audit_log)
    assert events == []


def test_clear_log_removes_file(audit_log):
    log_event("capture", log_file=audit_log)
    assert audit_log.exists()
    clear_log(audit_log)
    assert not audit_log.exists()


def test_clear_log_no_error_if_missing(audit_log):
    # Should not raise even if file doesn't exist
    clear_log(audit_log)
