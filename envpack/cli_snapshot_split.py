"""CLI commands for snapshot split."""

from __future__ import annotations

import sys
from pathlib import Path

from envpack.snapshot import load
from envpack.snapshot_split import SplitError, save_split, split_by_keys, split_by_prefix


def cmd_split(args) -> None:  # noqa: ANN001
    source = Path(args.snapshot)
    if not source.exists():
        print(f"error: snapshot not found: {source}", file=sys.stderr)
        sys.exit(1)

    try:
        snapshot = load(source)
    except Exception as exc:  # noqa: BLE001
        print(f"error: could not load snapshot: {exc}", file=sys.stderr)
        sys.exit(1)

    output_dir = Path(args.output_dir)
    base_name = args.base_name or source.stem

    if args.prefixes:
        prefixes = [p.strip() for p in args.prefixes.split(",") if p.strip()]
        parts = split_by_prefix(snapshot, prefixes, strip_prefix=args.strip_prefix)
    elif args.groups:
        groups: dict = {}
        for item in args.groups.split(";"):
            item = item.strip()
            if ":" not in item:
                print(f"error: invalid group spec '{item}' (expected name:KEY1,KEY2)", file=sys.stderr)
                sys.exit(1)
            name, keys_str = item.split(":", 1)
            groups[name.strip()] = [k.strip() for k in keys_str.split(",") if k.strip()]
        parts = split_by_keys(snapshot, groups)
    else:
        print("error: provide --prefixes or --groups", file=sys.stderr)
        sys.exit(1)

    written = save_split(parts, output_dir, base_name=base_name, skip_empty=not args.keep_empty)
    for group, path in sorted(written.items()):
        print(f"{group}: {path}")


def register_split_commands(subparsers) -> None:  # noqa: ANN001
    p = subparsers.add_parser("split", help="Split a snapshot into multiple files")
    p.add_argument("snapshot", help="Path to source snapshot JSON")
    p.add_argument("output_dir", help="Directory to write split snapshots")
    p.add_argument("--base-name", dest="base_name", default="", help="Base filename prefix")
    p.add_argument("--prefixes", default="", help="Comma-separated key prefixes")
    p.add_argument("--groups", default="", help="Semicolon-separated name:KEY1,KEY2 groups")
    p.add_argument("--strip-prefix", dest="strip_prefix", action="store_true",
                   help="Remove prefix from keys in output (prefix mode only)")
    p.add_argument("--keep-empty", dest="keep_empty", action="store_true",
                   help="Write files for empty groups too")
    p.set_defaults(func=cmd_split)
