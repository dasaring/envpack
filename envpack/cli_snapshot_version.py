"""CLI commands for snapshot versioning."""

from __future__ import annotations

import sys
from pathlib import Path

from envpack.snapshot_version import (
    add_version,
    list_versions,
    get_version,
    delete_version_history,
    all_version_names,
)


def cmd_version_add(args) -> None:
    store = Path(args.store)
    entry = add_version(args.name, args.snapshot, label=getattr(args, "label", None), store=store)
    label_info = f" [{entry['label']}]" if entry.get("label") else ""
    print(f"Recorded version of '{args.name}': {entry['snapshot']}{label_info}")


def cmd_version_list(args) -> None:
    store = Path(args.store)
    versions = list_versions(args.name, store=store)
    if not versions:
        print(f"No versions recorded for '{args.name}'.")
        return
    for i, entry in enumerate(versions):
        label = f" [{entry['label']}]" if entry.get("label") else ""
        print(f"  [{i}]{label} {entry['snapshot']}")


def cmd_version_get(args) -> None:
    store = Path(args.store)
    index = getattr(args, "index", -1)
    entry = get_version(args.name, index=index, store=store)
    if entry is None:
        print(f"No version found for '{args.name}' at index {index}.", file=sys.stderr)
        sys.exit(1)
    label = f" [{entry['label']}]" if entry.get("label") else ""
    print(f"{entry['snapshot']}{label}")


def cmd_version_delete(args) -> None:
    store = Path(args.store)
    removed = delete_version_history(args.name, store=store)
    if removed:
        print(f"Deleted version history for '{args.name}'.")
    else:
        print(f"No version history found for '{args.name}'.", file=sys.stderr)
        sys.exit(1)


def cmd_version_names(args) -> None:
    store = Path(args.store)
    names = all_version_names(store=store)
    if not names:
        print("No versioned snapshots.")
    for name in names:
        print(name)


def register_version_commands(subparsers, default_store: str = ".envpack_versions.json") -> None:
    p = subparsers.add_parser("version", help="Manage snapshot versions")
    sp = p.add_subparsers(dest="version_cmd")
    p.set_defaults(store=default_store)

    add_p = sp.add_parser("add", help="Record a new version")
    add_p.add_argument("name")
    add_p.add_argument("snapshot")
    add_p.add_argument("--label", default=None)
    add_p.add_argument("--store", default=default_store)
    add_p.set_defaults(func=cmd_version_add)

    list_p = sp.add_parser("list", help="List versions for a name")
    list_p.add_argument("name")
    list_p.add_argument("--store", default=default_store)
    list_p.set_defaults(func=cmd_version_list)

    get_p = sp.add_parser("get", help="Get a specific version")
    get_p.add_argument("name")
    get_p.add_argument("--index", type=int, default=-1)
    get_p.add_argument("--store", default=default_store)
    get_p.set_defaults(func=cmd_version_get)

    del_p = sp.add_parser("delete", help="Delete all versions for a name")
    del_p.add_argument("name")
    del_p.add_argument("--store", default=default_store)
    del_p.set_defaults(func=cmd_version_delete)

    names_p = sp.add_parser("names", help="List all versioned snapshot names")
    names_p.add_argument("--store", default=default_store)
    names_p.set_defaults(func=cmd_version_names)
