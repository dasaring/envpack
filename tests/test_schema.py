"""Tests for envpack.schema module."""

import json
import pytest
from pathlib import Path

from envpack.schema import (
    SchemaField,
    SchemaResult,
    load_schema,
    save_schema,
    validate_against_schema,
)


@pytest.fixture
def simple_schema():
    return {
        "DATABASE_URL": SchemaField(required=True, pattern=r"postgres://.+"),
        "PORT": SchemaField(required=True, pattern=r"\d+"),
        "DEBUG": SchemaField(required=False, pattern=r"true|false"),
    }


def test_valid_snapshot_passes(simple_schema):
    snapshot = {"DATABASE_URL": "postgres://localhost/db", "PORT": "5432"}
    result = validate_against_schema(snapshot, simple_schema)
    assert result.is_valid()
    assert result.summary() == "Schema valid."


def test_missing_required_key(simple_schema):
    snapshot = {"PORT": "5432"}
    result = validate_against_schema(snapshot, simple_schema)
    assert not result.is_valid()
    assert "DATABASE_URL" in result.missing_required


def test_optional_key_absent_is_ok(simple_schema):
    snapshot = {"DATABASE_URL": "postgres://localhost/db", "PORT": "5432"}
    result = validate_against_schema(snapshot, simple_schema)
    assert "DEBUG" not in result.missing_required
    assert result.is_valid()


def test_pattern_mismatch(simple_schema):
    snapshot = {"DATABASE_URL": "mysql://localhost/db", "PORT": "5432"}
    result = validate_against_schema(snapshot, simple_schema)
    assert not result.is_valid()
    assert "DATABASE_URL" in result.pattern_failures


def test_pattern_valid_optional_key(simple_schema):
    snapshot = {
        "DATABASE_URL": "postgres://localhost/db",
        "PORT": "5432",
        "DEBUG": "true",
    }
    result = validate_against_schema(snapshot, simple_schema)
    assert result.is_valid()


def test_unexpected_keys_allowed_by_default(simple_schema):
    snapshot = {"DATABASE_URL": "postgres://localhost/db", "PORT": "5432", "EXTRA": "x"}
    result = validate_against_schema(snapshot, simple_schema, allow_extra=True)
    assert result.is_valid()
    assert result.unexpected_keys == []


def test_unexpected_keys_disallowed(simple_schema):
    snapshot = {"DATABASE_URL": "postgres://localhost/db", "PORT": "5432", "EXTRA": "x"}
    result = validate_against_schema(snapshot, simple_schema, allow_extra=False)
    assert not result.is_valid()
    assert "EXTRA" in result.unexpected_keys


def test_summary_lists_all_issues(simple_schema):
    snapshot = {"DATABASE_URL": "mysql://bad", "EXTRA": "x"}
    result = validate_against_schema(snapshot, simple_schema, allow_extra=False)
    summary = result.summary()
    assert "PORT" in summary
    assert "DATABASE_URL" in summary
    assert "EXTRA" in summary


def test_save_and_load_schema(tmp_path, simple_schema):
    schema_path = tmp_path / "schema.json"
    save_schema(simple_schema, schema_path)
    assert schema_path.exists()
    loaded = load_schema(schema_path)
    assert set(loaded.keys()) == set(simple_schema.keys())
    assert loaded["DATABASE_URL"].required is True
    assert loaded["DATABASE_URL"].pattern == r"postgres://.+"
    assert loaded["DEBUG"].required is False


def test_load_schema_from_json(tmp_path):
    raw = {
        "API_KEY": {"required": True, "pattern": "[A-Z0-9]{32}", "description": "API key"},
        "TIMEOUT": {"required": False, "pattern": None, "description": ""},
    }
    path = tmp_path / "schema.json"
    path.write_text(json.dumps(raw))
    schema = load_schema(path)
    assert schema["API_KEY"].description == "API key"
    assert schema["TIMEOUT"].required is False
    assert schema["TIMEOUT"].pattern is None
