"""cli_snapshot_set.py — CLI commands for managing snapshot sets."""
from __future__ import annotations

import sys
from pathlib import Path

from envpack.snapshot_set import (
    add_snapshot_to_set,
    create_set,
    delete_set,
    get_set,
    list_sets,
    remove_snapshot_from_set,
)

_DEFAULT_STORE = Path(".envpack") / "snapshot_sets.json"


def cmd_set_create(args) -> None:
    store = Path(getattr(args, "store", _DEFAULT_STORE))
    entry = create_set(args.name, description=getattr(args, "description", ""), store=store)
    print(f"Created set '{entry['name']}'.")


def cmd_set_delete(args) -> None:
    store = Path(getattr(args, "store", _DEFAULT_STORE))
    removed = delete_set(args.name, store=store)
    if removed:
        print(f"Deleted set '{args.name}'.")
    else:
        print(f"Set '{args.name}' not found.", file=sys.stderr)
        sys.exit(1)


def cmd_set_add(args) -> None:
    store = Path(getattr(args, "store", _DEFAULT_STORE))
    try:
        added = add_snapshot_to_set(args.name, args.snapshot, store=store)
    except KeyError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
    if added:
        print(f"Added '{args.snapshot}' to set '{args.name}'.")
    else:
        print(f"'{args.snapshot}' already in set '{args.name}'.")


def cmd_set_remove(args) -> None:
    store = Path(getattr(args, "store", _DEFAULT_STORE))
    try:
        removed = remove_snapshot_from_set(args.name, args.snapshot, store=store)
    except KeyError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
    if removed:
        print(f"Removed '{args.snapshot}' from set '{args.name}'.")
    else:
        print(f"'{args.snapshot}' not found in set '{args.name}'.", file=sys.stderr)
        sys.exit(1)


def cmd_set_show(args) -> None:
    store = Path(getattr(args, "store", _DEFAULT_STORE))
    entry = get_set(args.name, store=store)
    if entry is None:
        print(f"Set '{args.name}' not found.", file=sys.stderr)
        sys.exit(1)
    print(f"Set: {entry['name']}")
    if entry["description"]:
        print(f"Description: {entry['description']}")
    snaps = entry["snapshots"]
    print(f"Snapshots ({len(snaps)}):")
    for s in snaps:
        print(f"  {s}")


def cmd_set_list(args) -> None:
    store = Path(getattr(args, "store", _DEFAULT_STORE))
    sets = list_sets(store=store)
    if not sets:
        print("No snapshot sets defined.")
        return
    for entry in sets:
        count = len(entry["snapshots"])
        desc = f" — {entry['description']}" if entry["description"] else ""
        print(f"{entry['name']} ({count} snapshot(s)){desc}")


def register_set_commands(subparsers) -> None:
    p = subparsers.add_parser("set-create", help="Create a snapshot set")
    p.add_argument("name")
    p.add_argument("--description", default="")
    p.set_defaults(func=cmd_set_create)

    p = subparsers.add_parser("set-delete", help="Delete a snapshot set")
    p.add_argument("name")
    p.set_defaults(func=cmd_set_delete)

    p = subparsers.add_parser("set-add", help="Add a snapshot to a set")
    p.add_argument("name")
    p.add_argument("snapshot")
    p.set_defaults(func=cmd_set_add)

    p = subparsers.add_parser("set-remove", help="Remove a snapshot from a set")
    p.add_argument("name")
    p.add_argument("snapshot")
    p.set_defaults(func=cmd_set_remove)

    p = subparsers.add_parser("set-show", help="Show contents of a set")
    p.add_argument("name")
    p.set_defaults(func=cmd_set_show)

    p = subparsers.add_parser("set-list", help="List all snapshot sets")
    p.set_defaults(func=cmd_set_list)
