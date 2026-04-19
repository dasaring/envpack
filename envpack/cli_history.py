"""CLI commands for snapshot history management."""

from __future__ import annotations

import argparse

from envpack import history


def cmd_history_record(args: argparse.Namespace) -> None:
    entry = history.record_snapshot(
        snapshot_path=args.snapshot,
        label=args.label,
        history_file=args.history_file,
    )
    label_str = f" [{entry['label']}]" if entry["label"] else ""
    print(f"Recorded: {entry['snapshot_path']}{label_str} at {entry['recorded_at']}")


def cmd_history_list(args: argparse.Namespace) -> None:
    entries = history.list_history(history_file=args.history_file)
    if not entries:
        print("No history entries found.")
        return
    for i, e in enumerate(entries, 1):
        label_str = f" [{e['label']}]" if e.get("label") else ""
        print(f"{i:3}. {e['snapshot_path']}{label_str}  ({e['recorded_at']})")


def cmd_history_find(args: argparse.Namespace) -> None:
    entries = history.find_by_label(args.label, history_file=args.history_file)
    if not entries:
        print(f"No entries found for label '{args.label}'.")
        return
    for e in entries:
        print(f"{e['snapshot_path']}  ({e['recorded_at']})")


def cmd_history_remove(args: argparse.Namespace) -> None:
    removed = history.remove_entry(args.snapshot, history_file=args.history_file)
    if removed:
        print(f"Removed history entry for: {args.snapshot}")
    else:
        print(f"No entry found for: {args.snapshot}")


def cmd_history_clear(args: argparse.Namespace) -> None:
    """Remove all entries from the history file after optional confirmation."""
    if not args.yes:
        confirm = input("Clear all history entries? [y/N] ").strip().lower()
        if confirm != "y":
            print("Aborted.")
            return
    count = history.clear_history(history_file=args.history_file)
    print(f"Cleared {count} history entry/entries.")


def register_history_commands(subparsers: argparse._SubParsersAction, history_file: str) -> None:
    p = subparsers.add_parser("history", help="Manage snapshot history")
    p.add_argument("--history-file", default=history_file)
    hs = p.add_subparsers(dest="history_cmd", required=True)

    rec = hs.add_parser("record", help="Record a snapshot in history")
    rec.add_argument("snapshot")
    rec.add_argument("--label", default=None)
    rec.set_defaults(func=cmd_history_record)

    ls = hs.add_parser("list", help="List history entries")
    ls.set_defaults(func=cmd_history_list)

    find = hs.add_parser("find", help="Find entries by label")
    find.add_argument("label")
    find.set_defaults(func=cmd_history_find)

    rm = hs.add_parser("remove", help="Remove a history entry")
    rm.add_argument("snapshot")
    rm.set_defaults(func=cmd_history_remove)

    clr = hs.add_parser("clear", help="Remove all history entries")
    clr.add_argument("-y", "--yes", action="store_true", help="Skip confirmation prompt")
    clr.set_defaults(func=cmd_history_clear)
