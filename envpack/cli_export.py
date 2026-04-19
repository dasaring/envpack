"""CLI commands for exporting snapshots."""
from __future__ import annotations
import argparse
import sys

from envpack.export import export_snapshot, SUPPORTED_FORMATS


def cmd_export(args: argparse.Namespace) -> None:
    fmt = args.format.lower()
    try:
        content = export_snapshot(
            snapshot_path=args.snapshot,
            fmt=fmt,
            output_path=args.output,
        )
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: snapshot file not found: {args.snapshot}", file=sys.stderr)
        sys.exit(1)
    except ImportError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.output:
        print(f"Exported to {args.output}")
    else:
        print(content, end="")


def register_export_commands(subparsers) -> None:
    p = subparsers.add_parser(
        "export",
        help="Export a snapshot to dotenv, JSON, or YAML format",
    )
    p.add_argument("snapshot", help="Path to snapshot JSON file")
    p.add_argument(
        "--format", "-f",
        choices=SUPPORTED_FORMATS,
        default="dotenv",
        help="Output format (default: dotenv)",
    )
    p.add_argument(
        "--output", "-o",
        default=None,
        help="Write output to this file instead of stdout",
    )
    p.set_defaults(func=cmd_export)
