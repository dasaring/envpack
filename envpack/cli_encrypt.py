"""CLI helpers for encrypted snapshot commands."""

import argparse
import getpass
import os
import sys
from typing import Optional

from envpack import snapshot as snap
from envpack.encrypt import save_encrypted, load_encrypted


def _get_passphrase(args_passphrase: Optional[str], confirm: bool = False) -> str:
    """Resolve passphrase from CLI arg, env var, or interactive prompt."""
    if args_passphrase:
        return args_passphrase
    env_pass = os.environ.get("ENVPACK_PASSPHRASE")
    if env_pass:
        return env_pass
    passphrase = getpass.getpass("Passphrase: ")
    if confirm:
        confirm_pass = getpass.getpass("Confirm passphrase: ")
        if passphrase != confirm_pass:
            print("Error: passphrases do not match.", file=sys.stderr)
            sys.exit(1)
    return passphrase


def cmd_capture_encrypted(args: argparse.Namespace) -> None:
    """Capture environment and save as an encrypted snapshot."""
    keys = args.keys if args.keys else None
    captured = snap.capture(keys=keys)
    passphrase = _get_passphrase(getattr(args, "passphrase", None), confirm=True)
    output = args.output or "snapshot.enc"
    save_encrypted(captured, output, passphrase)
    print(f"Encrypted snapshot saved to {output} ({len(captured)} variables).")


def cmd_restore_encrypted(args: argparse.Namespace) -> None:
    """Load an encrypted snapshot and emit export statements."""
    from envpack.restore import generate_export_script
    passphrase = _get_passphrase(getattr(args, "passphrase", None))
    try:
        data = load_encrypted(args.file, passphrase)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    shell = getattr(args, "shell", "bash")
    print(generate_export_script(data, shell=shell))


def register_encrypted_commands(subparsers: argparse._SubParsersAction) -> None:
    """Attach encrypted sub-commands to an existing ArgumentParser."""
    # capture-enc
    p_cap = subparsers.add_parser("capture-enc", help="Capture env to encrypted file")
    p_cap.add_argument("--output", "-o", default="snapshot.enc")
    p_cap.add_argument("--passphrase", "-p", default=None)
    p_cap.add_argument("--keys", nargs="*", metavar="KEY")
    p_cap.set_defaults(func=cmd_capture_encrypted)

    # restore-enc
    p_res = subparsers.add_parser("restore-enc", help="Restore env from encrypted file")
    p_res.add_argument("file")
    p_res.add_argument("--passphrase", "-p", default=None)
    p_res.add_argument("--shell", default="bash", choices=["bash", "fish"])
    p_res.set_defaults(func=cmd_restore_encrypted)
