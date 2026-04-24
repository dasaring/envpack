"""CLI commands for retention policy management."""

from __future__ import annotations

import sys
from pathlib import Path

from envpack.retention import (
    apply_policy,
    get_policy,
    list_policies,
    remove_policy,
    set_policy,
)

_DEFAULT_POLICY_FILE = Path(".envpack_retention.json")


def cmd_retention_set(args) -> None:
    policy_file = Path(getattr(args, "policy_file", _DEFAULT_POLICY_FILE))
    if args.max_count is None and args.max_age_days is None:
        print("Error: provide --max-count and/or --max-age-days.", file=sys.stderr)
        sys.exit(1)
    entry = set_policy(
        name=args.name,
        max_count=args.max_count,
        max_age_days=args.max_age_days,
        policy_file=policy_file,
    )
    parts = []
    if "max_count" in entry:
        parts.append(f"max_count={entry['max_count']}")
    if "max_age_days" in entry:
        parts.append(f"max_age_days={entry['max_age_days']}")
    print(f"Policy '{args.name}' set: {', '.join(parts)}")


def cmd_retention_remove(args) -> None:
    policy_file = Path(getattr(args, "policy_file", _DEFAULT_POLICY_FILE))
    removed = remove_policy(args.name, policy_file=policy_file)
    if removed:
        print(f"Policy '{args.name}' removed.")
    else:
        print(f"Policy '{args.name}' not found.", file=sys.stderr)
        sys.exit(1)


def cmd_retention_list(args) -> None:
    policy_file = Path(getattr(args, "policy_file", _DEFAULT_POLICY_FILE))
    policies = list_policies(policy_file=policy_file)
    if not policies:
        print("No retention policies defined.")
        return
    for p in policies:
        parts = [f"name={p['name']}"]
        if "max_count" in p:
            parts.append(f"max_count={p['max_count']}")
        if "max_age_days" in p:
            parts.append(f"max_age_days={p['max_age_days']}")
        print("  " + ", ".join(parts))


def cmd_retention_apply(args) -> None:
    policy_file = Path(getattr(args, "policy_file", _DEFAULT_POLICY_FILE))
    snapshots = [Path(s) for s in args.snapshots]
    try:
        to_prune = apply_policy(args.name, snapshots, policy_file=policy_file)
    except KeyError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
    if not to_prune:
        print("No snapshots to prune.")
        return
    for p in to_prune:
        if args.dry_run:
            print(f"[dry-run] would remove: {p}")
        else:
            p.unlink(missing_ok=True)
            print(f"Removed: {p}")


def register_retention_commands(subparsers) -> None:
    rp = subparsers.add_parser("retention", help="Manage retention policies")
    sub = rp.add_subparsers(dest="retention_cmd")

    p_set = sub.add_parser("set", help="Create or update a retention policy")
    p_set.add_argument("name")
    p_set.add_argument("--max-count", type=int, dest="max_count", default=None)
    p_set.add_argument("--max-age-days", type=int, dest="max_age_days", default=None)
    p_set.set_defaults(func=cmd_retention_set)

    p_rm = sub.add_parser("remove", help="Remove a retention policy")
    p_rm.add_argument("name")
    p_rm.set_defaults(func=cmd_retention_remove)

    p_ls = sub.add_parser("list", help="List all retention policies")
    p_ls.set_defaults(func=cmd_retention_list)

    p_apply = sub.add_parser("apply", help="Apply a policy to a list of snapshots")
    p_apply.add_argument("name")
    p_apply.add_argument("snapshots", nargs="+")
    p_apply.add_argument("--dry-run", action="store_true", default=False)
    p_apply.set_defaults(func=cmd_retention_apply)
