"""CLI commands for managing snapshot bookmarks."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envpack.bookmark import (
    add_bookmark,
    remove_bookmark,
    resolve_bookmark,
    list_bookmarks,
    clear_bookmarks,
)

_DEFAULT_STORE = Path.home() / ".envpack" / "bookmarks.json"


def cmd_bookmark_add(args: argparse.Namespace) -> None:
    store = Path(args.store)
    is_new = add_bookmark(args.name, args.path, store=store)
    verb = "Created" if is_new else "Updated"
    print(f"{verb} bookmark '{args.name}' -> {args.path}")


def cmd_bookmark_remove(args: argparse.Namespace) -> None:
    store = Path(args.store)
    removed = remove_bookmark(args.name, store=store)
    if removed:
        print(f"Removed bookmark '{args.name}'.")
    else:
        print(f"Bookmark '{args.name}' not found.", file=sys.stderr)
        sys.exit(1)


def cmd_bookmark_resolve(args: argparse.Namespace) -> None:
    store = Path(args.store)
    path = resolve_bookmark(args.name, store=store)
    if path is None:
        print(f"Bookmark '{args.name}' not found.", file=sys.stderr)
        sys.exit(1)
    print(path)


def cmd_bookmark_list(args: argparse.Namespace) -> None:
    store = Path(args.store)
    bookmarks = list_bookmarks(store=store)
    if not bookmarks:
        print("No bookmarks defined.")
        return
    for name, path in sorted(bookmarks.items()):
        print(f"  {name}: {path}")


def cmd_bookmark_clear(args: argparse.Namespace) -> None:
    store = Path(args.store)
    count = clear_bookmarks(store=store)
    print(f"Cleared {count} bookmark(s).")


def register_bookmark_commands(subparsers: argparse._SubParsersAction) -> None:
    store_kwargs = {"default": str(_DEFAULT_STORE), "help": "bookmarks store file"}

    p_add = subparsers.add_parser("bookmark-add", help="Add or update a bookmark")
    p_add.add_argument("name", help="Bookmark name")
    p_add.add_argument("path", help="Path to snapshot file")
    p_add.add_argument("--store", **store_kwargs)
    p_add.set_defaults(func=cmd_bookmark_add)

    p_rm = subparsers.add_parser("bookmark-remove", help="Remove a bookmark")
    p_rm.add_argument("name", help="Bookmark name")
    p_rm.add_argument("--store", **store_kwargs)
    p_rm.set_defaults(func=cmd_bookmark_remove)

    p_res = subparsers.add_parser("bookmark-resolve", help="Resolve a bookmark to its path")
    p_res.add_argument("name", help="Bookmark name")
    p_res.add_argument("--store", **store_kwargs)
    p_res.set_defaults(func=cmd_bookmark_resolve)

    p_ls = subparsers.add_parser("bookmark-list", help="List all bookmarks")
    p_ls.add_argument("--store", **store_kwargs)
    p_ls.set_defaults(func=cmd_bookmark_list)

    p_clr = subparsers.add_parser("bookmark-clear", help="Clear all bookmarks")
    p_clr.add_argument("--store", **store_kwargs)
    p_clr.set_defaults(func=cmd_bookmark_clear)
