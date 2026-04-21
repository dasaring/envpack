"""CLI commands for namespace management."""

from __future__ import annotations

import argparse
from pathlib import Path

from envpack.namespace import (
    add_to_namespace,
    find_namespace_for_snapshot,
    get_snapshots_in_namespace,
    list_namespaces,
    remove_from_namespace,
)


def cmd_ns_add(args: argparse.Namespace) -> None:
    ns_file = Path(args.ns_file)
    added = add_to_namespace(args.namespace, args.snapshot, ns_file)
    if added:
        print(f"Added '{args.snapshot}' to namespace '{args.namespace}'.")
    else:
        print(f"'{args.snapshot}' is already in namespace '{args.namespace}'.")


def cmd_ns_remove(args: argparse.Namespace) -> None:
    ns_file = Path(args.ns_file)
    removed = remove_from_namespace(args.namespace, args.snapshot, ns_file)
    if removed:
        print(f"Removed '{args.snapshot}' from namespace '{args.namespace}'.")
    else:
        print(f"'{args.snapshot}' was not found in namespace '{args.namespace}'.")


def cmd_ns_list(args: argparse.Namespace) -> None:
    ns_file = Path(args.ns_file)
    namespaces = list_namespaces(ns_file)
    if not namespaces:
        print("No namespaces defined.")
        return
    for ns in namespaces:
        print(ns)


def cmd_ns_show(args: argparse.Namespace) -> None:
    ns_file = Path(args.ns_file)
    snapshots = get_snapshots_in_namespace(args.namespace, ns_file)
    if not snapshots:
        print(f"Namespace '{args.namespace}' is empty or does not exist.")
        return
    for path in snapshots:
        print(path)


def cmd_ns_find(args: argparse.Namespace) -> None:
    ns_file = Path(args.ns_file)
    ns = find_namespace_for_snapshot(args.snapshot, ns_file)
    if ns:
        print(ns)
    else:
        print(f"No namespace found for '{args.snapshot}'.")


def register_namespace_commands(
    subparsers: argparse._SubParsersAction,
    ns_file: str = ".envpack_namespaces.json",
) -> None:
    common = {"ns_file": ns_file}

    p_add = subparsers.add_parser("ns-add", help="Add snapshot to a namespace")
    p_add.add_argument("namespace")
    p_add.add_argument("snapshot")
    p_add.set_defaults(func=cmd_ns_add, **common)

    p_rm = subparsers.add_parser("ns-remove", help="Remove snapshot from a namespace")
    p_rm.add_argument("namespace")
    p_rm.add_argument("snapshot")
    p_rm.set_defaults(func=cmd_ns_remove, **common)

    p_ls = subparsers.add_parser("ns-list", help="List all namespaces")
    p_ls.set_defaults(func=cmd_ns_list, **common)

    p_show = subparsers.add_parser("ns-show", help="Show snapshots in a namespace")
    p_show.add_argument("namespace")
    p_show.set_defaults(func=cmd_ns_show, **common)

    p_find = subparsers.add_parser("ns-find", help="Find namespace for a snapshot")
    p_find.add_argument("snapshot")
    p_find.set_defaults(func=cmd_ns_find, **common)
