import pytest
from envpack.merge import merge_snapshots, MergeConflictError


SNAP_A = {"HOME": "/home/alice", "EDITOR": "vim", "ONLY_A": "1"}
SNAP_B = {"HOME": "/home/bob", "SHELL": "zsh", "ONLY_B": "2"}
SNAP_C = {"HOME": "/home/carol", "EDITOR": "nano"}


def test_merge_empty_list():
    assert merge_snapshots([]) == {}


def test_merge_single_snapshot():
    assert merge_snapshots([SNAP_A]) == SNAP_A


def test_merge_last_strategy_default():
    result = merge_snapshots([SNAP_A, SNAP_B])
    assert result["HOME"] == "/home/bob"  # last wins
    assert result["ONLY_A"] == "1"
    assert result["ONLY_B"] == "2"


def test_merge_first_strategy():
    result = merge_snapshots([SNAP_A, SNAP_B], strategy="first")
    assert result["HOME"] == "/home/alice"  # first wins
    assert result["SHELL"] == "zsh"  # only in B, still included


def test_merge_last_strategy_explicit():
    result = merge_snapshots([SNAP_A, SNAP_C], strategy="last")
    assert result["EDITOR"] == "nano"
    assert result["HOME"] == "/home/carol"
    assert result["ONLY_A"] == "1"


def test_merge_error_strategy_no_conflict():
    snap_x = {"FOO": "1"}
    snap_y = {"BAR": "2"}
    result = merge_snapshots([snap_x, snap_y], strategy="error")
    assert result == {"FOO": "1", "BAR": "2"}


def test_merge_error_strategy_raises_on_conflict():
    with pytest.raises(MergeConflictError) as exc_info:
        merge_snapshots([SNAP_A, SNAP_B], strategy="error")
    assert "HOME" in exc_info.value.conflicts


def test_merge_error_strategy_lists_all_conflicts():
    with pytest.raises(MergeConflictError) as exc_info:
        merge_snapshots([SNAP_A, SNAP_C], strategy="error")
    conflicts = exc_info.value.conflicts
    assert "HOME" in conflicts
    assert "EDITOR" in conflicts


def test_merge_error_strategy_with_labels():
    with pytest.raises(MergeConflictError) as exc_info:
        merge_snapshots([SNAP_A, SNAP_B], strategy="error", labels=["prod", "dev"])
    conflicts = exc_info.value.conflicts
    assert "prod" in conflicts["HOME"]
    assert "dev" in conflicts["HOME"]


def test_merge_labels_length_mismatch():
    with pytest.raises(ValueError):
        merge_snapshots([SNAP_A, SNAP_B], labels=["only-one"])


def test_merge_three_snapshots_last():
    result = merge_snapshots([SNAP_A, SNAP_B, SNAP_C], strategy="last")
    assert result["HOME"] == "/home/carol"
    assert result["EDITOR"] == "nano"
    assert result["SHELL"] == "zsh"
    assert result["ONLY_A"] == "1"
    assert result["ONLY_B"] == "2"
