#!/usr/bin/env python3
"""
OMK Update Checker

Checks for updates to OMK from the GitHub repository.
"""

from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path


CURRENT_VERSION = "0.1.0"
REPO = "your-org/oh-my-kimi"


def check_for_updates() -> tuple[bool, str, str]:
    """Check if an update is available. Returns (update_available, current, latest)."""
    try:
        url = f"https://api.github.com/repos/{REPO}/releases/latest"
        req = urllib.request.Request(url, headers={"User-Agent": "OMK-Updater"})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
            latest = data.get("tag_name", "").lstrip("v")
            if latest and latest != CURRENT_VERSION:
                return True, CURRENT_VERSION, latest
    except Exception as e:
        print(f"Update check failed: {e}", file=sys.stderr)

    return False, CURRENT_VERSION, CURRENT_VERSION


def cli() -> int:
    """CLI entry point."""
    update_available, current, latest = check_for_updates()

    if update_available:
        print(f"Update available: {current} -> {latest}")
        print("Run: git pull && ./install.sh")
        return 0
    else:
        print(f"OMK is up to date ({current})")
        return 0


if __name__ == "__main__":
    sys.exit(cli())
