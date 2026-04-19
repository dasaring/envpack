"""CLI commands for snapshot validation."""
from __future__ import annotations
import argparse
import json
import sys
from envpack.snapshot import load
from envpack.validate import validate_snapshot


def cmd_validate(args: argparse.Namespace) -> None:
    snapshot = load(args.file)
    required = args.require or []
    forbidden = args.forbid or []
    result = validate_snapshot(
        snapshot,
        required_keys=required,
        forbidden_keys=forbidden,
        max_value_length=args.max_value_length,
    )
    print(result.summary())
    if not result.valid:
        sys.exit(1)


def register_validate_commands(subparsers) -> None:
    p = subparsers.add_parser("validate", help="Validate a snapshot file")
    p.add_argument("file", help="Path to snapshot JSON file")
    p.add_argument(
        "--require",
        metavar="KEY",
        nargs="+",
        help="Keys that must be present",
    )
    p.add_argument(
        "--forbid",
        metavar="KEY",
        nargs="+",
        help="Keys that must not be present",
    )
    p.add_argument(
        "--max-value-length",
        type=int,
        default=4096,
        dest="max_value_length",
        help="Maximum allowed value length (default: 4096)",
    )
    p.set_defaults(func=cmd_validate)
