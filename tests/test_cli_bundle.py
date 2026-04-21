"""Tests for envpack.cli_bundle CLI commands."""

import argparse
import json
import os
import sys
import pytest

from envpack.cli_bundle import cmd_bundle_create, cmd_bundle_extract, cmd_bundle_list


@pytest.fixture()
def snaps(tmp_path):
    a = tmp_path / "snap_a.json"
    b = tmp_path / "snap_b.json"
    a.write_text(json.dumps({"KEY": "val"}))
    b.write_text(json.dumps({"OTHER": "thing"}))
    return tmp_path, str(a), str(b)


def make_args(**kwargs):
    ns = argparse.Namespace(**kwargs)
    return ns


def test_cmd_create_prints_bundle_path(snaps, tmp_path, capsys):
    _, a, b = snaps
    out = str(tmp_path / "out.zip")
    args = make_args(snapshots=[a, b], output=out, label=None)
    cmd_bundle_create(args)
    captured = capsys.readouterr()
    assert "Bundle created" in captured.out
    assert "out.zip" in captured.out


def test_cmd_create_prints_label(snaps, tmp_path, capsys):
    _, a, _ = snaps
    out = str(tmp_path / "labeled.zip")
    args = make_args(snapshots=[a], output=out, label="release-1")
    cmd_bundle_create(args)
    captured = capsys.readouterr()
    assert "release-1" in captured.out


def test_cmd_create_missing_snapshot_exits_1(tmp_path):
    out = str(tmp_path / "bad.zip")
    args = make_args(snapshots=["/no/such/file.json"], output=out, label=None)
    with pytest.raises(SystemExit) as exc_info:
        cmd_bundle_create(args)
    assert exc_info.value.code == 1


def test_cmd_extract_prints_dest(snaps, tmp_path, capsys):
    _, a, b = snaps
    bundle = str(tmp_path / "env.zip")
    from envpack.bundle import create_bundle
    create_bundle([a, b], bundle)
    dest = str(tmp_path / "out")
    args = make_args(bundle=bundle, dest=dest)
    cmd_bundle_extract(args)
    captured = capsys.readouterr()
    assert "Extracted to" in captured.out


def test_cmd_extract_missing_bundle_exits_1(tmp_path):
    args = make_args(bundle=str(tmp_path / "ghost.zip"), dest=str(tmp_path / "out"))
    with pytest.raises(SystemExit) as exc_info:
        cmd_bundle_extract(args)
    assert exc_info.value.code == 1


def test_cmd_list_prints_snapshots(snaps, tmp_path, capsys):
    _, a, b = snaps
    bundle = str(tmp_path / "env.zip")
    from envpack.bundle import create_bundle
    create_bundle([a, b], bundle, label="v2")
    args = make_args(bundle=bundle)
    cmd_bundle_list(args)
    captured = capsys.readouterr()
    assert "snap_a.json" in captured.out
    assert "v2" in captured.out


def test_cmd_list_missing_bundle_exits_1(tmp_path):
    args = make_args(bundle=str(tmp_path / "ghost.zip"))
    with pytest.raises(SystemExit) as exc_info:
        cmd_bundle_list(args)
    assert exc_info.value.code == 1
