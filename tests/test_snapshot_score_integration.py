"""Integration tests for snapshot scoring end-to-end."""
import json
from pathlib import Path
import pytest

from envpack.snapshot_score import score_snapshot


@pytest.fixture
def snap_dir(tmp_path):
    return tmp_path


def _write(path: Path, data: dict) -> Path:
    path.write_text(json.dumps(data))
    return path


def test_perfect_score_clean_snapshot(snap_dir):
    """A snapshot with no secrets, no lint issues, and all required keys should score 100."""
    p = _write(snap_dir / "perfect.json", {"APP_ENV": "production", "LOG_LEVEL": "info"})
    result = score_snapshot(p, required_keys=["APP_ENV", "LOG_LEVEL"])
    assert result.total == result.max_score
    assert result.percent == 100.0
    assert result.notes == []


def test_low_score_empty_with_missing_required(snap_dir):
    p = _write(snap_dir / "bad.json", {})
    result = score_snapshot(p, required_keys=["DB_URL", "SECRET_KEY", "API_KEY"])
    assert result.percent < 50.0


def test_score_decreases_with_exposed_secret(snap_dir):
    clean = _write(snap_dir / "clean.json", {"APP": "v1"})
    dirty = _write(snap_dir / "dirty.json", {"APP": "v1", "SECRET_KEY": "abc123"})
    r_clean = score_snapshot(clean)
    r_dirty = score_snapshot(dirty)
    assert r_clean.total >= r_dirty.total


def test_score_result_is_serialisable(snap_dir):
    p = _write(snap_dir / "snap.json", {"X": "1"})
    result = score_snapshot(p)
    # Ensure breakdown dict is JSON-serialisable
    data = json.dumps({"total": result.total, "breakdown": result.breakdown})
    loaded = json.loads(data)
    assert loaded["total"] == result.total
