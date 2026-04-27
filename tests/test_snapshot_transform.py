"""Tests for envpack.snapshot_transform."""

import pytest

from envpack.snapshot_transform import (
    TransformError,
    apply_regex,
    rename_keys,
    transform_values,
)


SNAP = {
    "APP_NAME": "myapp",
    "DB_HOST": "  localhost  ",
    "SECRET_KEY": "AbCdEf",
}


# ---------------------------------------------------------------------------
# transform_values
# ---------------------------------------------------------------------------

def test_transform_upper_all_keys():
    result = transform_values(SNAP, "upper")
    assert result["APP_NAME"] == "MYAPP"
    assert result["SECRET_KEY"] == "ABCDEF"


def test_transform_lower_all_keys():
    result = transform_values(SNAP, "lower")
    assert result["APP_NAME"] == "myapp"
    assert result["SECRET_KEY"] == "abcdef"


def test_transform_strip_removes_whitespace():
    result = transform_values(SNAP, "strip")
    assert result["DB_HOST"] == "localhost"


def test_transform_reverse():
    result = transform_values({"KEY": "hello"}, "reverse")
    assert result["KEY"] == "olleh"


def test_transform_restricted_to_keys():
    result = transform_values(SNAP, "upper", keys=["APP_NAME"])
    assert result["APP_NAME"] == "MYAPP"
    # other keys must remain unchanged
    assert result["SECRET_KEY"] == "AbCdEf"


def test_transform_does_not_mutate_original():
    original = {"K": "value"}
    transform_values(original, "upper")
    assert original["K"] == "value"


def test_transform_unknown_operation_raises():
    with pytest.raises(TransformError, match="Unknown transform operation"):
        transform_values(SNAP, "nonexistent")


# ---------------------------------------------------------------------------
# rename_keys
# ---------------------------------------------------------------------------

def test_rename_keys_basic():
    snap = {"OLD_NAME": "val"}
    result = rename_keys(snap, {"OLD_NAME": "NEW_NAME"})
    assert "NEW_NAME" in result
    assert "OLD_NAME" not in result
    assert result["NEW_NAME"] == "val"


def test_rename_keys_preserves_untouched_keys():
    snap = {"A": "1", "B": "2"}
    result = rename_keys(snap, {"A": "AA"})
    assert "B" in result
    assert result["B"] == "2"


def test_rename_keys_missing_key_ignore_by_default():
    snap = {"X": "1"}
    # Should not raise when ignore_missing=True (default)
    result = rename_keys(snap, {"MISSING": "NEW"}, ignore_missing=True)
    assert result == {"X": "1"}


def test_rename_keys_missing_key_raises_when_strict():
    snap = {"X": "1"}
    with pytest.raises(TransformError, match="not found"):
        rename_keys(snap, {"MISSING": "NEW"}, ignore_missing=False)


def test_rename_keys_does_not_mutate_original():
    snap = {"OLD": "v"}
    rename_keys(snap, {"OLD": "NEW"})
    assert "OLD" in snap


# ---------------------------------------------------------------------------
# apply_regex
# ---------------------------------------------------------------------------

def test_apply_regex_replaces_pattern():
    snap = {"URL": "http://example.com"}
    result = apply_regex(snap, r"http", "https")
    assert result["URL"] == "https://example.com"


def test_apply_regex_restricted_to_keys():
    snap = {"A": "foo_bar", "B": "foo_baz"}
    result = apply_regex(snap, r"foo", "qux", keys=["A"])
    assert result["A"] == "qux_bar"
    assert result["B"] == "foo_baz"


def test_apply_regex_invalid_pattern_raises():
    with pytest.raises(TransformError, match="Invalid regex"):
        apply_regex({"K": "v"}, r"[", "x")


def test_apply_regex_does_not_mutate_original():
    snap = {"K": "hello world"}
    apply_regex(snap, r"world", "there")
    assert snap["K"] == "hello world"
