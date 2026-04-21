"""CLI commands for scope management."""

from __future__ import annotations

import argparse
from pathlib import Path

from envpack.scope import (
    add_to_scope,
    remove_from_scope,
    list_scopes,
    get_snapshots_in_scope,
    find_scope_for_snapshot,
)


def cmd_scope_add(args: argparse.Namespace) -> None:
    scope_file = Path(args.scope_file)
    added = add_to_scope(args.scope, args.snapshot, scope_file)
    if added:
        print(f"Added '{args.snapshot}' to scope '{args.scope}'.")
    else:
        print(f"'{args.snapshot}' already in scope '{args.scope}'.")


def cmd_scope_remove(args: argparse.Namespace) -> None:
    scope_file = Path(args.scope_file)
    removed = remove_from_scope(args.scope, args.snapshot, scope_file)
    if removed:
        print(f"Removed '{args.snapshot}' from scope '{args.scope}'.")
    else:
        print(f"'{args.snapshot}' not found in scope '{args.scope}'.")


def cmd_scope_list(args: argparse.Namespace) -> None:
    scope_file = Path(args.scope_file)
    scopes = list_scopes(scope_file)
    if not scopes:
        print("No scopes defined.")
    else:
        for s in scopes:
            print(s)


def cmd_scope_show(args: argparse.Namespace) -> None:
    scope_file = Path(args.scope_file)
    paths = get_snapshots_in_scope(args.scope, scope_file)
    if not paths:
        print(f"Scope '{args.scope}' is empty or does not exist.")
    else:
        for p in paths:
            print(p)


def cmd_scope_find(args: argparse.Namespace) -> None:
    scope_file = Path(args.scope_file)
    scope = find_scope_for_snapshot(args.snapshot, scope_file)
    if scope:
        print(scope)
    else:
        print(f"No scope found for '{args.snapshot}'.")


def register_scope_commands(subparsers: argparse._SubParsersAction, scope_file: str) -> None:
    common = {"scope_file": scope_file}

    p_add = subparsers.add_parser("scope-add", help="Add snapshot to a scope")
    p_add.add_argument("scope"); p_add.add_argument("snapshot")
    p_add.set_defaults(func=cmd_scope_add, **common)

    p_rm = subparsers.add_parser("scope-remove", help="Remove snapshot from a scope")
    p_rm.add_argument("scope"); p_rm.add_argument("snapshot")
    p_rm.set_defaults(func=cmd_scope_remove, **common)

    p_ls = subparsers.add_parser("scope-list", help="List all scopes")
    p_ls.set_defaults(func=cmd_scope_list, **common)

    p_show = subparsers.add_parser("scope-show", help="Show snapshots in a scope")
    p_show.add_argument("scope")
    p_show.set_defaults(func=cmd_scope_show, **common)

    p_find = subparsers.add_parser("scope-find", help="Find scope for a snapshot")
    p_find.add_argument("snapshot")
    p_find.set_defaults(func=cmd_scope_find, **common)
