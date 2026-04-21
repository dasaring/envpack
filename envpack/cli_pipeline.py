"""CLI commands for running snapshot pipelines."""

from __future__ import annotations

import argparse
import json
import sys

from envpack.pipeline import run_pipeline


def cmd_pipeline_run(args: argparse.Namespace) -> None:
    steps = [s.strip() for s in args.steps.split(",") if s.strip()]
    if not steps:
        print("error: --steps must be a non-empty comma-separated list", file=sys.stderr)
        sys.exit(1)

    try:
        result = run_pipeline(
            snapshot_path=args.snapshot,
            steps=steps,
            halt_on_error=args.halt_on_error,
            lint_allowed_keys=args.lint_allowed.split(",") if args.lint_allowed else [],
            validate_required=args.require.split(",") if args.require else [],
            export_format=args.export_format,
            export_path=args.export_path,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"pipeline aborted: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.output_json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(result.summary())

    sys.exit(0 if result.success else 1)


def register_pipeline_commands(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser(
        "pipeline",
        help="run a sequence of steps (lint, validate, export) against a snapshot",
    )
    p.add_argument("snapshot", help="path to the snapshot JSON file")
    p.add_argument(
        "--steps",
        default="lint,validate",
        help="comma-separated list of steps to run (lint, validate, export)",
    )
    p.add_argument(
        "--halt-on-error",
        action="store_true",
        help="stop pipeline on first failing step",
    )
    p.add_argument(
        "--lint-allowed",
        default="",
        help="comma-separated list of sensitive key names that are allowed",
    )
    p.add_argument(
        "--require",
        default="",
        help="comma-separated list of keys required by the validate step",
    )
    p.add_argument(
        "--export-format",
        default="json",
        choices=["json", "dotenv", "yaml"],
        help="output format for the export step",
    )
    p.add_argument(
        "--export-path",
        default=None,
        help="destination file for the export step",
    )
    p.add_argument(
        "--json",
        dest="output_json",
        action="store_true",
        help="print result as JSON",
    )
    p.set_defaults(func=cmd_pipeline_run)
