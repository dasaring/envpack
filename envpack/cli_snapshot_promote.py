"""CLI commands for snapshot promotion across environment stages."""

from __future__ import annotations

import sys
from pathlib import Path

from envpack.snapshot_promote import PromoteError, promote_snapshot, promotion_diff


def cmd_promote(args) -> None:
    """Promote a snapshot from one stage to another."""
    source = Path(args.source)
    dest = Path(args.dest)

    strip = list(args.strip) if args.strip else []
    add: dict[str, str] = {}
    for kv in args.add or []:
        if "=" not in kv:
            print(f"Error: --add value must be KEY=VALUE, got: {kv!r}", file=sys.stderr)
            sys.exit(1)
        k, v = kv.split("=", 1)
        add[k] = v

    if args.dry_run:
        if not source.exists():
            print(f"Error: source not found: {source}", file=sys.stderr)
            sys.exit(1)
        diff = promotion_diff(source, dest)
        print(f"Dry-run promotion: {source} -> {dest}")
        for category, keys in diff.items():
            if keys:
                print(f"  {category}: {', '.join(keys)}")
        return

    try:
        result = promote_snapshot(
            source,
            dest,
            overwrite=args.overwrite,
            strip_keys=strip,
            add_keys=add or None,
        )
        print(f"Promoted: {result}")
    except PromoteError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def register_promote_commands(subparsers) -> None:
    p = subparsers.add_parser("promote", help="Promote a snapshot to another stage")
    p.add_argument("source", help="Source snapshot path")
    p.add_argument("dest", help="Destination snapshot path")
    p.add_argument("--overwrite", action="store_true", help="Overwrite destination if it exists")
    p.add_argument(
        "--strip",
        metavar="KEY",
        nargs="+",
        help="Keys to remove from the promoted snapshot",
    )
    p.add_argument(
        "--add",
        metavar="KEY=VALUE",
        nargs="+",
        help="Extra key=value pairs to inject into the promoted snapshot",
    )
    p.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    p.set_defaults(func=cmd_promote)
