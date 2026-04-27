"""Tests for envpack.snapshot_score."""
import json
import pytest
from pathlib import Path

from envpack.snapshot_score import score_snapshot, ScoreResult


@pytest.fixture
def snap_dir(tmp_path):
    return tmp_path


def _write(path: Path, data: dict) -> Path:
    path.write_text(json.dumps(data))
    return path


def test_score_result_percent_zero_max():
    r = ScoreResult(path="x", total=0, max_score=0)
    assert r.percent == 0.0


def test_score_result_percent():
    r = ScoreResult(path="x", total=50, max_score=100)
    assert r.percent == 50.0


def test_score_result_summary_contains_score():
    r = ScoreResult(path="x", total=80, max_score=100, notes=["a note"])
    s = r.summary()
    assert "80/100" in s
    assert "a note" in s


def test_empty_snapshot_loses_non_empty_points(snap_dir):
    p = _write(snap_dir / "empty.json", {})
    result = score_snapshot(p)
    assert result.breakdown["non_empty"] == 0
    assert any("empty" in n.lower() for n in result.notes)


def test_non_empty_snapshot_gets_non_empty_points(snap_dir):
    p = _write(snap_dir / "snap.json", {"APP_ENV": "production"})
    result = score_snapshot(p)
    assert result.breakdown["non_empty"] == 10


def test_clean_snapshot_gets_full_lint_score(snap_dir):
    p = _write(snap_dir / "clean.json", {"APP_ENV": "prod", "LOG_LEVEL": "info"})
    result = score_snapshot(p)
    assert result.breakdown["lint_clean"] == 30


def test_sensitive_key_with_real_value_loses_points(snap_dir):
    p = _write(snap_dir / "secret.json", {"SECRET_KEY": "mysupersecret"})
    result = score_snapshot(p)
    assert result.breakdown["no_exposed_secrets"] < 30
    assert any("sensitive" in n.lower() for n in result.notes)


def test_required_keys_all_present(snap_dir):
    p = _write(snap_dir / "snap.json", {"FOO": "1", "BAR": "2"})
    result = score_snapshot(p, required_keys=["FOO", "BAR"])
    assert result.breakdown["required_keys"] == 30


def test_required_keys_missing_loses_points(snap_dir):
    p = _write(snap_dir / "snap.json", {"FOO": "1"})
    result = score_snapshot(p, required_keys=["FOO", "BAR", "BAZ"])
    assert result.breakdown["required_keys"] < 30
    assert any("Missing" in n for n in result.notes)


def test_no_required_keys_gets_full_required_score(snap_dir):
    p = _write(snap_dir / "snap.json", {"X": "1"})
    result = score_snapshot(p, required_keys=None)
    assert result.breakdown["required_keys"] == 30


def test_total_does_not_exceed_max(snap_dir):
    p = _write(snap_dir / "snap.json", {"APP": "v1"})
    result = score_snapshot(p)
    assert result.total <= result.max_score


def test_missing_file_raises(snap_dir):
    with pytest.raises(FileNotFoundError):
        score_snapshot(snap_dir / "nonexistent.json")
