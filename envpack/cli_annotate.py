"""CLI commands for snapshot annotations."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envpack.snapshot_annotate import (
    annotate,
    remove_annotation,
    get_annotations,
    find_by_annotation,
    clear_annotations,
)


def cmd_annotate_set(args: argparse.Namespace) -> None:
    store = Path(args.store)
    is_new = annotate(args.snapshot, args.key, args.value, store=store)
    action = "added" if is_new else "updated"
    print(f"Annotation {action}: {args.key}={args.value!r} on {args.snapshot}")


def cmd_annotate_remove(args: argparse.Namespace) -> None:
    store = Path(args.store)
    removed = remove_annotation(args.snapshot, args.key, store=store)
    if removed:
        print(f"Removed annotation '{args.key}' from {args.snapshot}")
    else:
        print(f"Annotation '{args.key}' not found on {args.snapshot}", file=sys.stderr)
        sys.exit(1)


def cmd_annotate_show(args: argparse.Namespace) -> None:
    store = Path(args.store)
    annotations = get_annotations(args.snapshot, store=store)
    if not annotations:
        print(f"No annotations for {args.snapshot}")
        return
    for k, v in sorted(annotations.items()):
        print(f"{k}={v}")


def cmd_annotate_find(args: argparse.Namespace) -> None:
    store = Path(args.store)
    results = find_by_annotation(args.key, args.value or None, store=store)
    if not results:
        print("No snapshots found.")
        return
    for snap, val in sorted(results.items()):
        print(f"{snap}  ({args.key}={val})")


def cmd_annotate_clear(args: argparse.Namespace) -> None:
    store = Path(args.store)
    count = clear_annotations(args.snapshot, store=store)
    print(f"Cleared {count} annotation(s) from {args.snapshot}")


def register_annotate_commands(subparsers: argparse._SubParsersAction, default_store: str) -> None:
    p = subparsers.add_parser("annotate", help="Manage snapshot annotations")
    sp = p.add_subparsers(dest="annotate_cmd", required=True)

    def _base(name, help_text):
        cmd = sp.add_parser(name, help=help_text)
        cmd.add_argument("--store", default=default_store)
        return cmd

    s = _base("set", "Add or update an annotation")
    s.add_argument("snapshot")
    s.add_argument("key")
    s.add_argument("value")
    s.set_defaults(func=cmd_annotate_set)

    r = _base("remove", "Remove an annotation key")
    r.add_argument("snapshot")
    r.add_argument("key")
    r.set_defaults(func=cmd_annotate_remove)

    sh = _base("show", "Show all annotations for a snapshot")
    sh.add_argument("snapshot")
    sh.set_defaults(func=cmd_annotate_show)

    f = _base("find", "Find snapshots by annotation key/value")
    f.add_argument("key")
    f.add_argument("value", nargs="?", default=None)
    f.set_defaults(func=cmd_annotate_find)

    cl = _base("clear", "Remove all annotations for a snapshot")
    cl.add_argument("snapshot")
    cl.set_defaults(func=cmd_annotate_clear)
