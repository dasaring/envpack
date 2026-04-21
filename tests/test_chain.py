"""Tests for envpack.chain."""
from __future__ import annotations

import json
import pytest
from pathlib import Path

from envpack.chain import build_chain, save_chain, describe_chain, ChainError


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def snap_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(directory: Path, name: str, data: dict) -> Path:
    p = directory / name
    p.write_text(json.dumps(data))
    return p


# ---------------------------------------------------------------------------
# build_chain
# ---------------------------------------------------------------------------

def test_build_chain_empty_list_raises(snap_dir):
    with pytest.raises(ChainError, match="at least one entry"):
        build_chain([])


def test_build_chain_missing_file_raises(snap_dir):
    with pytest.raises(ChainError, match="not found"):
        build_chain([snap_dir / "ghost.json"])


def test_build_chain_single_snapshot(snap_dir):
    p = _write(snap_dir, "a.json", {"FOO": "1", "BAR": "2"})
    result = build_chain([p])
    assert result == {"FOO": "1", "BAR": "2"}


def test_build_chain_later_wins(snap_dir):
    a = _write(snap_dir, "a.json", {"FOO": "base", "ONLY_A": "yes"})
    b = _write(snap_dir, "b.json", {"FOO": "override", "ONLY_B": "yes"})
    result = build_chain([a, b])
    assert result["FOO"] == "override"
    assert result["ONLY_A"] == "yes"
    assert result["ONLY_B"] == "yes"


def test_build_chain_three_layers(snap_dir):
    a = _write(snap_dir, "a.json", {"K": "a"})
    b = _write(snap_dir, "b.json", {"K": "b", "L": "b"})
    c = _write(snap_dir, "c.json", {"K": "c"})
    result = build_chain([a, b, c])
    assert result["K"] == "c"
    assert result["L"] == "b"


# ---------------------------------------------------------------------------
# save_chain
# ---------------------------------------------------------------------------

def test_save_chain_creates_file(snap_dir):
    a = _write(snap_dir, "a.json", {"X": "1"})
    out = snap_dir / "merged.json"
    returned = save_chain([a], out)
    assert returned == out
    assert out.exists()


def test_save_chain_content_is_valid_json(snap_dir):
    a = _write(snap_dir, "a.json", {"X": "1"})
    out = snap_dir / "merged.json"
    save_chain([a], out)
    data = json.loads(out.read_text())
    assert data["X"] == "1"


def test_save_chain_stores_label(snap_dir):
    a = _write(snap_dir, "a.json", {"X": "1"})
    out = snap_dir / "merged.json"
    save_chain([a], out, label="my-chain")
    data = json.loads(out.read_text())
    assert data["__chain_label__"] == "my-chain"


def test_save_chain_stores_sources(snap_dir):
    a = _write(snap_dir, "a.json", {"X": "1"})
    b = _write(snap_dir, "b.json", {"Y": "2"})
    out = snap_dir / "merged.json"
    save_chain([a, b], out)
    data = json.loads(out.read_text())
    assert len(data["__chain_sources__"]) == 2


# ---------------------------------------------------------------------------
# describe_chain
# ---------------------------------------------------------------------------

def test_describe_chain_empty():
    result = describe_chain([])
    assert "Empty chain" in result


def test_describe_chain_includes_filenames(snap_dir):
    a = _write(snap_dir, "base.json", {"A": "1"})
    b = _write(snap_dir, "override.json", {"A": "2", "B": "3"})
    result = describe_chain([a, b])
    assert "base.json" in result
    assert "override.json" in result


def test_describe_chain_shows_total(snap_dir):
    a = _write(snap_dir, "a.json", {"A": "1", "B": "2"})
    b = _write(snap_dir, "b.json", {"C": "3"})
    result = describe_chain([a, b])
    assert "Total keys in merged result: 3" in result
