"""CLI commands for snapshot bundling."""

import argparse
import sys

from envpack.bundle import create_bundle, extract_bundle, list_bundle, BundleError


def cmd_bundle_create(args: argparse.Namespace) -> None:
    """Pack snapshots into a bundle archive."""
    try:
        manifest = create_bundle(
            snapshot_paths=args.snapshots,
            bundle_path=args.output,
            label=args.label,
        )
        print(f"Bundle created: {args.output}")
        print(f"  Snapshots: {', '.join(manifest['snapshots'])}")
        if manifest.get("label"):
            print(f"  Label: {manifest['label']}")
    except BundleError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_bundle_extract(args: argparse.Namespace) -> None:
    """Extract snapshots from a bundle archive."""
    try:
        manifest = extract_bundle(args.bundle, args.dest)
        print(f"Extracted to: {args.dest}")
        print(f"  Snapshots: {', '.join(manifest['snapshots'])}")
    except BundleError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_bundle_list(args: argparse.Namespace) -> None:
    """List contents of a bundle archive."""
    try:
        manifest = list_bundle(args.bundle)
        label = manifest.get("label") or "(none)"
        print(f"Label: {label}")
        print("Snapshots:")
        for name in manifest.get("snapshots", []):
            print(f"  {name}")
    except BundleError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def register_bundle_commands(subparsers: argparse._SubParsersAction) -> None:
    """Register bundle sub-commands onto an existing subparsers object."""
    # create
    p_create = subparsers.add_parser("bundle-create", help="Pack snapshots into a bundle")
    p_create.add_argument("snapshots", nargs="+", help="Snapshot files to include")
    p_create.add_argument("--output", "-o", required=True, help="Output bundle path (.zip)")
    p_create.add_argument("--label", "-l", default=None, help="Optional label for the bundle")
    p_create.set_defaults(func=cmd_bundle_create)

    # extract
    p_extract = subparsers.add_parser("bundle-extract", help="Extract snapshots from a bundle")
    p_extract.add_argument("bundle", help="Bundle file to extract")
    p_extract.add_argument("--dest", "-d", default=".", help="Destination directory")
    p_extract.set_defaults(func=cmd_bundle_extract)

    # list
    p_list = subparsers.add_parser("bundle-list", help="List contents of a bundle")
    p_list.add_argument("bundle", help="Bundle file to inspect")
    p_list.set_defaults(func=cmd_bundle_list)
