"""CLI commands for snapshot alias management."""

from __future__ import annotations

import argparse
from pathlib import Path

from envpack.alias import (
    add_alias,
    list_aliases,
    remove_alias,
    resolve_alias,
)

_DEFAULT_ALIAS_FILE = Path(".envpack_aliases.json")


def cmd_alias_add(args: argparse.Namespace) -> None:
    alias_file = Path(args.alias_file)
    is_new = add_alias(args.name, args.snapshot, alias_file)
    verb = "Created" if is_new else "Updated"
    print(f"{verb} alias '{args.name}' -> {args.snapshot}")


def cmd_alias_remove(args: argparse.Namespace) -> None:
    alias_file = Path(args.alias_file)
    ok = remove_alias(args.name, alias_file)
    if ok:
        print(f"Removed alias '{args.name}'.")
    else:
        print(f"Alias '{args.name}' not found.")


def cmd_alias_resolve(args: argparse.Namespace) -> None:
    alias_file = Path(args.alias_file)
    path = resolve_alias(args.name, alias_file)
    if path is None:
        print(f"No alias named '{args.name}'.")
    else:
        print(path)


def cmd_alias_list(args: argparse.Namespace) -> None:
    alias_file = Path(args.alias_file)
    aliases = list_aliases(alias_file)
    if not aliases:
        print("No aliases registered.")
        return
    width = max(len(k) for k in aliases)
    for name, path in sorted(aliases.items()):
        print(f"  {name:<{width}}  ->  {path}")


def register_alias_commands(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--alias-file",
        default=str(_DEFAULT_ALIAS_FILE),
        help="Path to the alias registry file",
    )

    p_add = subparsers.add_parser("alias-add", parents=[common], help="Add or update an alias")
    p_add.add_argument("name", help="Alias name")
    p_add.add_argument("snapshot", help="Path to the snapshot file")
    p_add.set_defaults(func=cmd_alias_add)

    p_rm = subparsers.add_parser("alias-remove", parents=[common], help="Remove an alias")
    p_rm.add_argument("name", help="Alias name to remove")
    p_rm.set_defaults(func=cmd_alias_remove)

    p_res = subparsers.add_parser("alias-resolve", parents=[common], help="Resolve an alias to its path")
    p_res.add_argument("name", help="Alias name to resolve")
    p_res.set_defaults(func=cmd_alias_resolve)

    p_ls = subparsers.add_parser("alias-list", parents=[common], help="List all aliases")
    p_ls.set_defaults(func=cmd_alias_list)
