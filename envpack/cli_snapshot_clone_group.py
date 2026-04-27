"""CLI commands for snapshot clone groups."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envpack.snapshot_clone_group import (
    add_snapshot_to_group,
    create_group,
    delete_group,
    get_group,
    list_groups,
    remove_snapshot_from_group,
)

_DEFAULT_STORE = Path(".envpack") / "clone_groups.json"


def cmd_group_create(args: argparse.Namespace) -> None:
    store = Path(args.store)
    entry = create_group(args.name, description=args.description or "", store=store)
    print(f"Created clone group '{entry['name']}'.")


def cmd_group_delete(args: argparse.Namespace) -> None:
    store = Path(args.store)
    if delete_group(args.name, store=store):
        print(f"Deleted clone group '{args.name}'.")
    else:
        print(f"Clone group '{args.name}' not found.", file=sys.stderr)
        sys.exit(1)


def cmd_group_add(args: argparse.Namespace) -> None:
    store = Path(args.store)
    try:
        added = add_snapshot_to_group(args.name, args.snapshot, store=store)
    except KeyError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
    if added:
        print(f"Added '{args.snapshot}' to group '{args.name}'.")
    else:
        print(f"'{args.snapshot}' already in group '{args.name}'.")


def cmd_group_remove(args: argparse.Namespace) -> None:
    store = Path(args.store)
    try:
        removed = remove_snapshot_from_group(args.name, args.snapshot, store=store)
    except KeyError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
    if removed:
        print(f"Removed '{args.snapshot}' from group '{args.name}'.")
    else:
        print(f"'{args.snapshot}' not in group '{args.name}'.")


def cmd_group_show(args: argparse.Namespace) -> None:
    store = Path(args.store)
    entry = get_group(args.name, store=store)
    if entry is None:
        print(f"Clone group '{args.name}' not found.", file=sys.stderr)
        sys.exit(1)
    print(f"Group: {entry['name']}")
    if entry["description"]:
        print(f"  Description: {entry['description']}")
    if entry["snapshots"]:
        for snap in entry["snapshots"]:
            print(f"  - {snap}")
    else:
        print("  (no snapshots)")


def cmd_group_list(args: argparse.Namespace) -> None:
    store = Path(args.store)
    groups = list_groups(store=store)
    if not groups:
        print("No clone groups defined.")
        return
    for g in groups:
        count = len(g["snapshots"])
        print(f"{g['name']} ({count} snapshot{'s' if count != 1 else ''})")


def register_clone_group_commands(subparsers: argparse._SubParsersAction) -> None:
    common = {"default": str(_DEFAULT_STORE)}

    p = subparsers.add_parser("group-create", help="Create a clone group")
    p.add_argument("name")
    p.add_argument("--description", default="")
    p.add_argument("--store", **common)
    p.set_defaults(func=cmd_group_create)

    p = subparsers.add_parser("group-delete", help="Delete a clone group")
    p.add_argument("name")
    p.add_argument("--store", **common)
    p.set_defaults(func=cmd_group_delete)

    p = subparsers.add_parser("group-add", help="Add snapshot to a clone group")
    p.add_argument("name")
    p.add_argument("snapshot")
    p.add_argument("--store", **common)
    p.set_defaults(func=cmd_group_add)

    p = subparsers.add_parser("group-remove", help="Remove snapshot from a clone group")
    p.add_argument("name")
    p.add_argument("snapshot")
    p.add_argument("--store", **common)
    p.set_defaults(func=cmd_group_remove)

    p = subparsers.add_parser("group-show", help="Show a clone group")
    p.add_argument("name")
    p.add_argument("--store", **common)
    p.set_defaults(func=cmd_group_show)

    p = subparsers.add_parser("group-list", help="List all clone groups")
    p.add_argument("--store", **common)
    p.set_defaults(func=cmd_group_list)
