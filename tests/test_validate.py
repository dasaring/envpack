"""Tests for envpack.validate."""
import pytest
from envpack.validate import validate_snapshot, ValidationResult


def test_valid_snapshot():
    snap = {"HOME": "/home/user", "PATH": "/usr/bin"}
    result = validate_snapshot(snap)
    assert result.valid is True
    assert result.errors == []


def test_invalid_key_name():
    snap = {"123BAD": "value"}
    result = validate_snapshot(snap)
    assert result.valid is False
    assert any("123BAD" in e for e in result.errors)


def test_key_with_hyphen_invalid():
    snap = {"MY-VAR": "val"}
    result = validate_snapshot(snap)
    assert result.valid is False


def test_required_key_missing():
    snap = {"FOO": "bar"}
    result = validate_snapshot(snap, required_keys=["FOO", "MISSING"])
    assert result.valid is False
    assert any("MISSING" in e for e in result.errors)


def test_required_key_present():
    snap = {"FOO": "bar", "BAZ": "qux"}
    result = validate_snapshot(snap, required_keys=["FOO"])
    assert result.valid is True


def test_forbidden_key_absent():
    snap = {"FOO": "bar"}
    result = validate_snapshot(snap, forbidden_keys=["SECRET"])
    assert result.valid is True


def test_forbidden_key_present():
    snap = {"SECRET": "abc"}
    result = validate_snapshot(snap, forbidden_keys=["SECRET"])
    assert result.valid is False
    assert any("SECRET" in e for e in result.errors)


def test_value_too_long_warning():
    snap = {"BIG": "x" * 5000}
    result = validate_snapshot(snap, max_value_length=4096)
    assert result.valid is True
    assert any("BIG" in w for w in result.warnings)


def test_summary_valid():
    result = ValidationResult(valid=True)
    assert "valid" in result.summary().lower()


def test_summary_invalid():
    result = ValidationResult(valid=False, errors=["Missing key 'X'"])
    assert "INVALID" in result.summary()
    assert "Missing key" in result.summary()


def test_empty_snapshot_valid():
    result = validate_snapshot({})
    assert result.valid is True
