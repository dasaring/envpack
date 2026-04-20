"""Tests for envpack.template."""
import json
import pytest
from pathlib import Path

from envpack.template import (
    PLACEHOLDER,
    fill_template,
    load_template,
    save_template,
    to_template,
    unfilled_keys,
)


SAMPLE = {
    "HOME": "/home/user",
    "API_KEY": "super-secret",
    "DB_PASSWORD": "hunter2",
    "APP_NAME": "envpack",
    "AUTH_TOKEN": "tok_abc123",
}


def test_to_template_masks_sensitive_auto():
    tmpl = to_template(SAMPLE)
    assert tmpl["API_KEY"] == PLACEHOLDER
    assert tmpl["DB_PASSWORD"] == PLACEHOLDER
    assert tmpl["AUTH_TOKEN"] == PLACEHOLDER


def test_to_template_preserves_non_sensitive():
    tmpl = to_template(SAMPLE)
    assert tmpl["HOME"] == "/home/user"
    assert tmpl["APP_NAME"] == "envpack"


def test_to_template_explicit_keys():
    tmpl = to_template({"FOO": "bar", "BAZ": "qux"}, sensitive_keys=["FOO"], mask_auto=False)
    assert tmpl["FOO"] == PLACEHOLDER
    assert tmpl["BAZ"] == "qux"


def test_to_template_mask_auto_false_skips_auto():
    tmpl = to_template(SAMPLE, mask_auto=False)
    assert tmpl["API_KEY"] == "super-secret"


def test_save_and_load_template(tmp_path):
    tmpl = to_template(SAMPLE)
    dest = tmp_path / "template.json"
    save_template(tmpl, dest)
    assert dest.exists()
    loaded = load_template(dest)
    assert loaded == tmpl


def test_save_template_is_valid_json(tmp_path):
    dest = tmp_path / "t.json"
    save_template({"A": "1"}, dest)
    data = json.loads(dest.read_text())
    assert data == {"A": "1"}


def test_fill_template_replaces_placeholders():
    tmpl = {"API_KEY": PLACEHOLDER, "HOME": "/home/user"}
    filled = fill_template(tmpl, {"API_KEY": "real-key"})
    assert filled["API_KEY"] == "real-key"
    assert filled["HOME"] == "/home/user"


def test_fill_template_leaves_unfilled_without_strict():
    tmpl = {"API_KEY": PLACEHOLDER}
    filled = fill_template(tmpl, {})
    assert filled["API_KEY"] == PLACEHOLDER


def test_fill_template_strict_raises_on_missing():
    tmpl = {"API_KEY": PLACEHOLDER}
    with pytest.raises(ValueError, match="API_KEY"):
        fill_template(tmpl, {}, strict=True)


def test_unfilled_keys():
    tmpl = {"A": PLACEHOLDER, "B": "ok", "C": PLACEHOLDER}
    assert set(unfilled_keys(tmpl)) == {"A", "C"}


def test_unfilled_keys_empty_when_all_filled():
    tmpl = {"A": "1", "B": "2"}
    assert unfilled_keys(tmpl) == []
