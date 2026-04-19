#!/usr/bin/env python3
"""
OMK Notification Module

Python wrapper for sending notifications via Telegram, Discord, and Slack.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def get_script_dir() -> Path:
    """Get the directory containing notification scripts."""
    return Path(__file__).parent.parent / "scripts"


def send_notification(platform: str, message: str) -> bool:
    """Send a notification to the specified platform."""
    script = get_script_dir() / "notify.sh"
    if not script.exists():
        print(f"Notification script not found: {script}")
        return False

    try:
        result = subprocess.run(
            [str(script), f"--{platform}", message],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            print(f"Notification failed: {result.stderr}")
            return False
        print(result.stdout.strip())
        return True
    except Exception as e:
        print(f"Notification error: {e}")
        return False


def cli() -> int:
    """CLI for notifications."""
    if len(sys.argv) < 3:
        print("Usage: python3 -m omk.notifier <telegram|discord|slack> '<message>'")
        return 1

    platform = sys.argv[1]
    message = sys.argv[2]

    if platform not in ("telegram", "discord", "slack"):
        print(f"Unknown platform: {platform}")
        return 1

    return 0 if send_notification(platform, message) else 1


if __name__ == "__main__":
    sys.exit(cli())
