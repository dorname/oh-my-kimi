#!/usr/bin/env python3
"""
OMK CLI

Command-line interface for OMK utilities.
"""

from __future__ import annotations

import argparse
import sys

from .state import cli as state_cli


def main() -> int:
    parser = argparse.ArgumentParser(prog="omk", description="OMK CLI utilities")
    subparsers = parser.add_subparsers(dest="command")

    # State subcommand
    state_parser = subparsers.add_parser("state", help="State management")
    state_parser.add_argument("action", choices=["read", "write", "clear", "list"])
    state_parser.add_argument("mode", nargs="?")
    state_parser.add_argument("data", nargs="?")

    # Notifier subcommand
    notifier_parser = subparsers.add_parser("notifier", help="Send notifications")
    notifier_parser.add_argument("platform", choices=["telegram", "discord", "slack"])
    notifier_parser.add_argument("message")

    # Updater subcommand
    subparsers.add_parser("updater", help="Check for OMK updates")

    args = parser.parse_args()

    if args.command == "state":
        if args.action in ("read", "write", "clear") and not args.mode:
            print(f"Usage: omk state {args.action} <mode>")
            return 1
        if args.action == "write" and not args.data:
            print("Usage: omk state write <mode> '<json_data>'")
            return 1

        sys.argv = ["omk", args.action, args.mode or "", args.data or ""]
        return state_cli()

    if args.command == "notifier":
        from .notifier import send_notification
        return 0 if send_notification(args.platform, args.message) else 1

    if args.command == "updater":
        from .updater import cli as updater_cli
        return updater_cli()

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
