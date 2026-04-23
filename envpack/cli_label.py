"""CLI sub-commands for label management."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envpack.label import add_label, list_labels, remove_label, resolve_label


def cmd_label_add(args: argparse.Namespace) -> None:
    store = Path(args.store)
    is_new = add_label(args.label, args.path, store)
    action = "Created" if is_new else "Updated"
    print(f"{action} label '{args.label}' -> {args.path}")


def cmd_label_remove(args: argparse.Namespace) -> None:
    store = Path(args.store)
    ok = remove_label(args.label, store)
    if ok:
        print(f"Removed label '{args.label}'.")
    else:
        print(f"Label '{args.label}' not found.", file=sys.stderr)
        sys.exit(1)


def cmd_label_resolve(args: argparse.Namespace) -> None:
    store = Path(args.store)
    path = resolve_label(args.label, store)
    if path is None:
        print(f"Label '{args.label}' not found.", file=sys.stderr)
        sys.exit(1)
    print(path)


def cmd_label_list(args: argparse.Namespace) -> None:
    store = Path(args.store)
    entries = list_labels(store)
    if not entries:
        print("No labels defined.")
        return
    for entry in entries:
        print(f"{entry['label']:30s}  {entry['path']}")


def register_label_commands(subparsers: argparse._SubParsersAction, default_store: str) -> None:
    p = subparsers.add_parser("label", help="Manage snapshot labels")
    p.add_argument("--store", default=default_store)
    sp = p.add_subparsers(dest="label_cmd", required=True)

    pa = sp.add_parser("add", help="Add or update a label")
    pa.add_argument("label")
    pa.add_argument("path")
    pa.set_defaults(func=cmd_label_add)

    pr = sp.add_parser("remove", help="Remove a label")
    pr.add_argument("label")
    pr.set_defaults(func=cmd_label_remove)

    pres = sp.add_parser("resolve", help="Resolve a label to its path")
    pres.add_argument("label")
    pres.set_defaults(func=cmd_label_resolve)

    pl = sp.add_parser("list", help="List all labels")
    pl.set_defaults(func=cmd_label_list)
