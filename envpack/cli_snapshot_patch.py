"""CLI commands for patching snapshot files."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envpack.snapshot_patch import PatchError, patch_file


def cmd_patch(args: argparse.Namespace) -> None:
    path = Path(args.snapshot)
    if not path.exists():
        print(f"error: snapshot not found: {path}", file=sys.stderr)
        sys.exit(1)

    set_pairs: dict[str, str] = {}
    for item in args.set or []:
        if "=" not in item:
            print(f"error: --set value must be KEY=VALUE, got: {item!r}", file=sys.stderr)
            sys.exit(1)
        k, _, v = item.partition("=")
        set_pairs[k] = v

    rename_pairs: dict[str, str] = {}
    for item in args.rename or []:
        if ":" not in item:
            print(
                f"error: --rename value must be OLD:NEW, got: {item!r}", file=sys.stderr
            )
            sys.exit(1)
        old, _, new = item.partition(":")
        rename_pairs[old] = new

    dest = Path(args.dest) if args.dest else None

    try:
        out = patch_file(
            path,
            set=set_pairs or None,
            unset=args.unset or None,
            rename=rename_pairs or None,
            overwrite_rename=args.overwrite_rename,
            dest=dest,
        )
    except PatchError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(out)


def register_patch_commands(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("patch", help="Apply set/unset/rename operations to a snapshot")
    p.add_argument("snapshot", help="Path to the snapshot file")
    p.add_argument(
        "--set", metavar="KEY=VALUE", action="append", help="Set a key (repeatable)"
    )
    p.add_argument(
        "--unset", metavar="KEY", action="append", help="Remove a key (repeatable)"
    )
    p.add_argument(
        "--rename",
        metavar="OLD:NEW",
        action="append",
        help="Rename a key (repeatable)",
    )
    p.add_argument(
        "--overwrite-rename",
        action="store_true",
        default=False,
        help="Allow rename to overwrite an existing key",
    )
    p.add_argument("--dest", metavar="PATH", help="Output path (default: in-place)")
    p.set_defaults(func=cmd_patch)
