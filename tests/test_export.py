"""Tests for envpack.export."""
from __future__ import annotations
import json
import os
import pytest

from envpack.export import to_dotenv, to_json, export_snapshot


SAMPLE = {"HOME": "/home/user", "PATH": "/usr/bin:/bin", "DEBUG": "true"}


# --- to_dotenv ---

def test_dotenv_basic():
    result = to_dotenv({"FOO": "bar"})
    assert 'FOO="bar"' in result


def test_dotenv_sorted():
    result = to_dotenv({"Z": "1", "A": "2"})
    lines = [l for l in result.splitlines() if l]
    assert lines[0].startswith("A=")
    assert lines[1].startswith("Z=")


def test_dotenv_escapes_quotes():
    result = to_dotenv({"MSG": 'say "hello"'})
    assert 'MSG="say \\"hello\\""' in result


def test_dotenv_escapes_newline():
    result = to_dotenv({"ML": "line1\nline2"})
    assert "\\n" in result


def test_dotenv_empty_snapshot():
    assert to_dotenv({}) == ""


# --- to_json ---

def test_json_valid():
    result = to_json(SAMPLE)
    parsed = json.loads(result)
    assert parsed == SAMPLE


def test_json_sorted_keys():
    result = to_json({"Z": "1", "A": "2"})
    parsed = json.loads(result)
    assert list(parsed.keys()) == sorted(parsed.keys())


# --- export_snapshot ---

def test_export_dotenv(tmp_path):
    snap = tmp_path / "snap.json"
    snap.write_text(json.dumps({"FOO": "bar"}), encoding="utf-8")
    result = export_snapshot(str(snap), "dotenv")
    assert 'FOO="bar"' in result


def test_export_json(tmp_path):
    snap = tmp_path / "snap.json"
    snap.write_text(json.dumps({"FOO": "bar"}), encoding="utf-8")
    result = export_snapshot(str(snap), "json")
    assert json.loads(result) == {"FOO": "bar"}


def test_export_writes_file(tmp_path):
    snap = tmp_path / "snap.json"
    snap.write_text(json.dumps({"FOO": "bar"}), encoding="utf-8")
    out = tmp_path / "out.env"
    export_snapshot(str(snap), "dotenv", str(out))
    assert out.exists()
    assert 'FOO="bar"' in out.read_text()


def test_export_invalid_format(tmp_path):
    snap = tmp_path / "snap.json"
    snap.write_text(json.dumps({"A": "1"}), encoding="utf-8")
    with pytest.raises(ValueError, match="Unsupported format"):
        export_snapshot(str(snap), "toml")


def test_export_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        export_snapshot(str(tmp_path / "missing.json"), "dotenv")
