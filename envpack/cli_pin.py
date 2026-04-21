"""CLI commands for snapshot pin management."""

from __future__ import annotations

import argparse
from pathlib import Path

from envpack.pin import (
    pin_snapshot,
    unpin_snapshot,
    is_pinned,
    list_pins,
    clear_pins,
)

_DEFAULT_PIN_FILE = Path(".envpack_pins.json")


def cmd_pin_add(args: argparse.Namespace) -> None:
    pin_file = Path(args.pin_file)
    if pin_snapshot(args.snapshot, pin_file):
        print(f"Pinned: {args.snapshot}")
    else:
        print(f"Already pinned: {args.snapshot}")


def cmd_pin_remove(args: argparse.Namespace) -> None:
    pin_file = Path(args.pin_file)
    if unpin_snapshot(args.snapshot, pin_file):
        print(f"Unpinned: {args.snapshot}")
    else:
        print(f"Not pinned: {args.snapshot}")


def cmd_pin_list(args: argparse.Namespace) -> None:
    pin_file = Path(args.pin_file)
    pins = list_pins(pin_file)
    if not pins:
        print("No pinned snapshots.")
    else:
        for p in pins:
            print(p)


def cmd_pin_check(args: argparse.Namespace) -> None:
    pin_file = Path(args.pin_file)
    if is_pinned(args.snapshot, pin_file):
        print(f"PINNED: {args.snapshot}")
    else:
        print(f"NOT PINNED: {args.snapshot}")


def cmd_pin_clear(args: argparse.Namespace) -> None:
    pin_file = Path(args.pin_file)
    count = clear_pins(pin_file)
    print(f"Cleared {count} pin(s).")


def register_pin_commands(subparsers: argparse._SubParsersAction) -> None:
    def _add_common(p: argparse.ArgumentParser) -> None:
        p.add_argument("--pin-file", default=str(_DEFAULT_PIN_FILE), help="Path to pin index file")

    p_add = subparsers.add_parser("pin-add", help="Pin a snapshot")
    p_add.add_argument("snapshot", help="Path to snapshot file")
    _add_common(p_add)
    p_add.set_defaults(func=cmd_pin_add)

    p_rm = subparsers.add_parser("pin-remove", help="Unpin a snapshot")
    p_rm.add_argument("snapshot", help="Path to snapshot file")
    _add_common(p_rm)
    p_rm.set_defaults(func=cmd_pin_remove)

    p_ls = subparsers.add_parser("pin-list", help="List all pinned snapshots")
    _add_common(p_ls)
    p_ls.set_defaults(func=cmd_pin_list)

    p_chk = subparsers.add_parser("pin-check", help="Check if a snapshot is pinned")
    p_chk.add_argument("snapshot", help="Path to snapshot file")
    _add_common(p_chk)
    p_chk.set_defaults(func=cmd_pin_check)

    p_clr = subparsers.add_parser("pin-clear", help="Clear all pins")
    _add_common(p_clr)
    p_clr.set_defaults(func=cmd_pin_clear)
