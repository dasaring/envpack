"""CLI commands for snapshot lineage tracking."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envpack import snapshot_lineage as lin


def cmd_lineage_set(args: argparse.Namespace) -> None:
    store = Path(args.store)
    is_new = lin.set_parent(args.snapshot, args.parent, store=store)
    verb = "Linked" if is_new else "Updated"
    print(f"{verb}: {args.snapshot} -> {args.parent}")


def cmd_lineage_remove(args: argparse.Namespace) -> None:
    store = Path(args.store)
    removed = lin.remove_parent(args.snapshot, store=store)
    if removed:
        print(f"Removed lineage for: {args.snapshot}")
    else:
        print(f"No lineage record found for: {args.snapshot}", file=sys.stderr)
        sys.exit(1)


def cmd_lineage_parent(args: argparse.Namespace) -> None:
    store = Path(args.store)
    parent = lin.get_parent(args.snapshot, store=store)
    if parent is None:
        print(f"No parent recorded for: {args.snapshot}", file=sys.stderr)
        sys.exit(1)
    print(parent)


def cmd_lineage_children(args: argparse.Namespace) -> None:
    store = Path(args.store)
    children = lin.get_children(args.snapshot, store=store)
    if not children:
        print("No children found.")
    else:
        for c in children:
            print(c)


def cmd_lineage_ancestors(args: argparse.Namespace) -> None:
    store = Path(args.store)
    chain = lin.ancestors(args.snapshot, store=store)
    if not chain:
        print("No ancestors found.")
    else:
        for a in chain:
            print(a)


def register_lineage_commands(subparsers: argparse._SubParsersAction, default_store: str) -> None:
    p = subparsers.add_parser("lineage", help="Manage snapshot lineage")
    sp = p.add_subparsers(dest="lineage_cmd", required=True)

    def _common(sub):
        sub.add_argument("snapshot", help="Snapshot path")
        sub.add_argument("--store", default=default_store)

    s = sp.add_parser("set", help="Set parent of snapshot")
    _common(s)
    s.add_argument("parent", help="Parent snapshot path")
    s.set_defaults(func=cmd_lineage_set)

    r = sp.add_parser("remove", help="Remove lineage record")
    _common(r)
    r.set_defaults(func=cmd_lineage_remove)

    pa = sp.add_parser("parent", help="Show parent of snapshot")
    _common(pa)
    pa.set_defaults(func=cmd_lineage_parent)

    ch = sp.add_parser("children", help="Show children of snapshot")
    _common(ch)
    ch.set_defaults(func=cmd_lineage_children)

    an = sp.add_parser("ancestors", help="Show ancestor chain")
    _common(an)
    an.set_defaults(func=cmd_lineage_ancestors)
