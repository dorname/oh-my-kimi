#!/usr/bin/env bash
#
# OMK Update Checker
# Checks for updates to OMK and reports status.
#
# Usage:
#   ./update-check.sh
#   ./update-check.sh --quiet

set -euo pipefail

REPO="your-org/oh-my-kimi"
CURRENT_VERSION="0.1.0"

QUIET=0
if [[ "${1:-}" == "--quiet" ]]; then
    QUIET=1
fi

check_update() {
    if ! command -v curl &>/dev/null; then
        echo "Error: curl not found"
        exit 1
    fi

    LATEST=$(curl -s "https://api.github.com/repos/$REPO/releases/latest" | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/' || echo "")

    if [[ -z "$LATEST" ]]; then
        [[ "$QUIET" -eq 0 ]] && echo "Could not check for updates"
        exit 1
    fi

    if [[ "$LATEST" != "v$CURRENT_VERSION" && "$LATEST" != "$CURRENT_VERSION" ]]; then
        [[ "$QUIET" -eq 0 ]] && echo "Update available: $CURRENT_VERSION -> $LATEST"
        [[ "$QUIET" -eq 0 ]] && echo "Run: git pull && ./install.sh"
        exit 0
    else
        [[ "$QUIET" -eq 0 ]] && echo "OMK is up to date ($CURRENT_VERSION)"
        exit 0
    fi
}

check_update
