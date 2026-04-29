"""CLI commands for snapshot flattening / prefix operations."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from envpack.snapshot import load
from envpack.snapshot_flatten import (
    FlattenError,
    group_by_prefix,
    prefix_keys,
    save_groups,
    strip_prefix,
)


def cmd_flatten_group(args) -> None:
    """Group snapshot keys by prefix and write one file per group."""
    snap = load(Path(args.snapshot))
    groups = group_by_prefix(snap, sep=args.sep)
    output_dir = Path(args.output_dir)
    saved = save_groups(groups, output_dir)
    for path in sorted(saved):
        print(path)


def cmd_flatten_prefix(args) -> None:
    """Add a prefix to all keys in a snapshot and write the result."""
    try:
        snap = load(Path(args.snapshot))
        result = prefix_keys(snap, args.prefix, sep=args.sep)
        dest = Path(args.output)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(result, indent=2, sort_keys=True))
        print(dest)
    except FlattenError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_flatten_strip(args) -> None:
    """Strip a prefix from all matching keys and write the result."""
    try:
        snap = load(Path(args.snapshot))
        result = strip_prefix(snap, args.prefix, sep=args.sep)
        dest = Path(args.output)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(result, indent=2, sort_keys=True))
        print(dest)
    except FlattenError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)


def register_flatten_commands(subparsers) -> None:
    # flatten group
    p_group = subparsers.add_parser("flatten-group", help="Group snapshot keys by prefix")
    p_group.add_argument("snapshot")
    p_group.add_argument("output_dir")
    p_group.add_argument("--sep", default="_")
    p_group.set_defaults(func=cmd_flatten_group)

    # flatten prefix-add
    p_prefix = subparsers.add_parser("flatten-prefix", help="Add prefix to all keys")
    p_prefix.add_argument("snapshot")
    p_prefix.add_argument("prefix")
    p_prefix.add_argument("output")
    p_prefix.add_argument("--sep", default="_")
    p_prefix.set_defaults(func=cmd_flatten_prefix)

    # flatten strip
    p_strip = subparsers.add_parser("flatten-strip", help="Strip prefix from keys")
    p_strip.add_argument("snapshot")
    p_strip.add_argument("prefix")
    p_strip.add_argument("output")
    p_strip.add_argument("--sep", default="_")
    p_strip.set_defaults(func=cmd_flatten_strip)
