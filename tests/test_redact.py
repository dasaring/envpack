"""Tests for envpack.redact."""

import pytest
from envpack.redact import (
    DEFAULT_MASK,
    is_sensitive_key,
    redact_snapshot,
    redacted_keys,
)


# ---------------------------------------------------------------------------
# is_sensitive_key
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("key", [
    "PASSWORD", "db_password", "API_KEY", "api-key",
    "SECRET", "AUTH_TOKEN", "PRIVATE_KEY", "access_key",
    "AWS_SECRET_ACCESS_KEY", "GITHUB_TOKEN", "CREDENTIALS",
])
def test_sensitive_key_detected(key):
    assert is_sensitive_key(key) is True


@pytest.mark.parametrize("key", [
    "HOME", "PATH", "USER", "LANG", "PORT", "DATABASE_URL", "DEBUG",
])
def test_non_sensitive_key_not_detected(key):
    assert is_sensitive_key(key) is False


# ---------------------------------------------------------------------------
# redact_snapshot
# ---------------------------------------------------------------------------

def test_redact_replaces_sensitive_values():
    snap = {"API_KEY": "abc123", "HOME": "/home/user"}
    result = redact_snapshot(snap)
    assert result["API_KEY"] == DEFAULT_MASK
    assert result["HOME"] == "/home/user"


def test_redact_does_not_mutate_original():
    snap = {"PASSWORD": "s3cr3t", "USER": "alice"}
    original = dict(snap)
    redact_snapshot(snap)
    assert snap == original


def test_redact_custom_mask():
    snap = {"DB_PASSWORD": "hunter2"}
    result = redact_snapshot(snap, mask="[hidden]")
    assert result["DB_PASSWORD"] == "[hidden]"


def test_redact_extra_keys_are_redacted():
    snap = {"MY_CUSTOM_VAR": "value", "OTHER": "ok"}
    result = redact_snapshot(snap, extra_keys=["MY_CUSTOM_VAR"])
    assert result["MY_CUSTOM_VAR"] == DEFAULT_MASK
    assert result["OTHER"] == "ok"


def test_redact_allow_keys_skips_redaction():
    snap = {"API_KEY": "public-key", "SECRET": "still-secret"}
    result = redact_snapshot(snap, allow_keys=["API_KEY"])
    assert result["API_KEY"] == "public-key"
    assert result["SECRET"] == DEFAULT_MASK


def test_redact_empty_snapshot():
    assert redact_snapshot({}) == {}


# ---------------------------------------------------------------------------
# redacted_keys
# ---------------------------------------------------------------------------

def test_redacted_keys_returns_sorted_list():
    snap = {"TOKEN": "x", "HOME": "/", "PASSWORD": "y", "USER": "bob"}
    keys = redacted_keys(snap)
    assert keys == sorted(["TOKEN", "PASSWORD"])


def test_redacted_keys_respects_allow_keys():
    snap = {"TOKEN": "x", "PASSWORD": "y"}
    keys = redacted_keys(snap, allow_keys=["TOKEN"])
    assert keys == ["PASSWORD"]


def test_redacted_keys_extra_keys_included():
    snap = {"CUSTOM": "val", "NORMAL": "ok"}
    keys = redacted_keys(snap, extra_keys=["CUSTOM"])
    assert "CUSTOM" in keys
    assert "NORMAL" not in keys
