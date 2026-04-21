"""Tests for envpack.lint."""

import pytest
from envpack.lint import lint_snapshot, LintResult, LintWarning, MAX_VALUE_LENGTH


def test_clean_snapshot_returns_no_warnings():
    snap = {"HOME": "/home/user", "EDITOR": "vim", "LANG": "en_US.UTF-8"}
    result = lint_snapshot(snap)
    assert result.is_clean
    assert result.warnings == []


def test_sensitive_key_detected():
    snap = {"DB_PASSWORD": "s3cr3t"}
    result = lint_snapshot(snap)
    codes = [w.code for w in result.warnings]
    assert "SENSITIVE_KEY" in codes


def test_sensitive_key_variants():
    sensitive_keys = ["API_KEY", "AUTH_TOKEN", "PRIVATE_KEY", "MY_SECRET", "PASSWD"]
    for key in sensitive_keys:
        result = lint_snapshot({key: "value"})
        codes = [w.code for w in result.warnings]
        assert "SENSITIVE_KEY" in codes, f"Expected SENSITIVE_KEY warning for {key}"


def test_sensitive_key_allowed_skips_warning():
    snap = {"DB_PASSWORD": "s3cr3t"}
    result = lint_snapshot(snap, allowed_sensitive=["DB_PASSWORD"])
    codes = [w.code for w in result.warnings]
    assert "SENSITIVE_KEY" not in codes


def test_placeholder_value_detected():
    snap = {"API_URL": "CHANGE_ME"}
    result = lint_snapshot(snap)
    codes = [w.code for w in result.warnings]
    assert "PLACEHOLDER_VALUE" in codes


def test_placeholder_variants():
    placeholders = ["TODO", "PLACEHOLDER", "YOUR_VALUE_HERE", "<your-token>"]
    for val in placeholders:
        result = lint_snapshot({"SOME_KEY": val})
        codes = [w.code for w in result.warnings]
        assert "PLACEHOLDER_VALUE" in codes, f"Expected PLACEHOLDER_VALUE for {val!r}"


def test_empty_value_detected():
    snap = {"EMPTY_KEY": ""}
    result = lint_snapshot(snap)
    codes = [w.code for w in result.warnings]
    assert "EMPTY_VALUE" in codes


def test_empty_value_check_disabled():
    snap = {"EMPTY_KEY": ""}
    result = lint_snapshot(snap, check_empty_values=False)
    codes = [w.code for w in result.warnings]
    assert "EMPTY_VALUE" not in codes


def test_value_too_long_detected():
    snap = {"BIG_VAR": "x" * (MAX_VALUE_LENGTH + 1)}
    result = lint_snapshot(snap)
    codes = [w.code for w in result.warnings]
    assert "VALUE_TOO_LONG" in codes


def test_value_at_max_length_is_ok():
    snap = {"BIG_VAR": "x" * MAX_VALUE_LENGTH}
    result = lint_snapshot(snap)
    codes = [w.code for w in result.warnings]
    assert "VALUE_TOO_LONG" not in codes


def test_multiple_warnings_same_key():
    # A key that is sensitive AND has a placeholder value
    snap = {"API_TOKEN": "CHANGE_ME"}
    result = lint_snapshot(snap)
    codes = [w.code for w in result.warnings]
    assert "SENSITIVE_KEY" in codes
    assert "PLACEHOLDER_VALUE" in codes


def test_summary_clean():
    result = lint_snapshot({"HOME": "/home/user"})
    assert result.summary() == "No lint warnings."


def test_summary_with_warnings():
    snap = {"DB_PASSWORD": ""}
    result = lint_snapshot(snap)
    summary = result.summary()
    assert "warning" in summary.lower()
    assert "DB_PASSWORD" in summary


def test_to_dict_clean():
    result = lint_snapshot({"HOME": "/home/user"})
    d = result.to_dict()
    assert d["clean"] is True
    assert d["warnings"] == []


def test_to_dict_with_warnings():
    snap = {"SECRET_KEY": "abc"}
    result = lint_snapshot(snap)
    d = result.to_dict()
    assert d["clean"] is False
    assert len(d["warnings"]) >= 1
    assert all("key" in w and "code" in w and "message" in w for w in d["warnings"])
