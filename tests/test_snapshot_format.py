"""Tests for envpack.snapshot_format."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envpack.snapshot_format import (
    FormatError,
    convert_file,
    snapshot_to_dotenv,
    snapshot_to_json,
)


# ---------------------------------------------------------------------------
# snapshot_to_json
# ---------------------------------------------------------------------------

def test_to_json_is_valid_json():
    snap = {"B": "2", "A": "1"}
    result = json.loads(snapshot_to_json(snap))
    assert result == snap


def test_to_json_sorted_keys():
    snap = {"Z": "z", "A": "a", "M": "m"}
    text = snapshot_to_json(snap)
    keys = list(json.loads(text).keys())
    assert keys == sorted(keys)


def test_to_json_empty_snapshot():
    assert snapshot_to_json({}) == "{}"


# ---------------------------------------------------------------------------
# snapshot_to_dotenv
# ---------------------------------------------------------------------------

def test_dotenv_basic():
    snap = {"KEY": "value"}
    assert 'KEY="value"' in snapshot_to_dotenv(snap)


def test_dotenv_sorted_output():
    snap = {"Z": "z", "A": "a"}
    lines = snapshot_to_dotenv(snap).strip().splitlines()
    assert lines[0].startswith("A=")
    assert lines[1].startswith("Z=")


def test_dotenv_escapes_double_quotes():
    snap = {"MSG": 'say "hello"'}
    result = snapshot_to_dotenv(snap)
    assert '\\"hello\\"' in result


def test_dotenv_escapes_newlines():
    snap = {"MULTI": "line1\nline2"}
    result = snapshot_to_dotenv(snap)
    assert "\\n" in result
    assert "\n" not in result.split("=", 1)[1]


def test_dotenv_empty_snapshot():
    assert snapshot_to_dotenv({}) == ""


# ---------------------------------------------------------------------------
# convert_file
# ---------------------------------------------------------------------------

@pytest.fixture()
def snap_file(tmp_path):
    data = {"HOST": "localhost", "PORT": "5432"}
    p = tmp_path / "env.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    return p


def test_convert_to_json(snap_file, tmp_path):
    dest = tmp_path / "out.json"
    result = convert_file(snap_file, dest, "json")
    assert result == dest
    loaded = json.loads(dest.read_text())
    assert loaded["HOST"] == "localhost"


def test_convert_to_dotenv(snap_file, tmp_path):
    dest = tmp_path / ".env"
    convert_file(snap_file, dest, "dotenv")
    content = dest.read_text()
    assert 'HOST="localhost"' in content
    assert 'PORT="5432"' in content


def test_convert_creates_parent_dirs(snap_file, tmp_path):
    dest = tmp_path / "nested" / "deep" / "out.env"
    convert_file(snap_file, dest, "dotenv")
    assert dest.exists()


def test_convert_unsupported_format_raises(snap_file, tmp_path):
    with pytest.raises(FormatError, match="Unsupported format"):
        convert_file(snap_file, tmp_path / "out.toml", "toml")
