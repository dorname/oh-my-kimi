#!/usr/bin/env bash
#
# OMK Legacy Installations Cleanup
# Removes leftover omk binaries from previous cargo install / npm install setups.
# This script is for one-time cleanup only — OMK no longer supports these install methods.
#
# Usage:
#   ./cleanup-legacy.sh        # Interactive cleanup with confirmation
#   ./cleanup-legacy.sh --force # Skip confirmation
#   ./cleanup-legacy.sh --dry-run # Preview only

set -euo pipefail

FORCE=0
DRY_RUN=0

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
GRAY='\033[0;90m'
NC='\033[0m'

usage() {
    cat <<EOF
OMK Legacy Installations Cleanup

Removes leftover omk binaries from cargo install / npm install.
OMK no longer supports these install methods; this is a one-time cleanup.

Usage: $0 [OPTIONS]

Options:
  --force     Skip confirmation prompt
  --dry-run   Show what would be removed without making changes
  --help      Show this help message
EOF
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --force)
                FORCE=1
                shift
                ;;
            --dry-run)
                DRY_RUN=1
                shift
                ;;
            --help|-h)
                usage
                exit 0
                ;;
            *)
                echo -e "${RED}Unknown option: $1${NC}"
                usage
                exit 1
                ;;
        esac
    done
}

cleanup_cargo() {
    local cargo_bin="${CARGO_HOME:-$HOME/.cargo}/bin/omk"
    if [[ ! -f "$cargo_bin" ]]; then
        return 0
    fi

    if [[ "$DRY_RUN" -eq 1 ]]; then
        echo -e "  ${GRAY}→${NC}  Would remove $cargo_bin"
        return 0
    fi

    rm -f "$cargo_bin"
    echo -e "  ${GREEN}✓${NC}  Removed $cargo_bin"
}

cleanup_npm() {
    local npm_global_bin=""
    if command -v npm &>/dev/null; then
        npm_global_bin="$(npm prefix -g 2>/dev/null)/bin" || true
    fi

    if [[ -z "$npm_global_bin" || ! -d "$npm_global_bin" ]]; then
        return 0
    fi

    local npm_omk="$npm_global_bin/omk"
    if [[ ! -f "$npm_omk" ]]; then
        return 0
    fi

    if [[ "$DRY_RUN" -eq 1 ]]; then
        echo -e "  ${GRAY}→${NC}  Would remove $npm_omk"
        return 0
    fi

    rm -f "$npm_omk"
    echo -e "  ${GREEN}✓${NC}  Removed $npm_omk"
}

main() {
    parse_args "$@"

    echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║      OMK Legacy Installations Cleanup                     ║${NC}"
    echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
    echo ""

    if [[ "$DRY_RUN" -eq 1 ]]; then
        echo -e "${YELLOW}DRY RUN — no changes will be made${NC}\n"
    fi

    # Detect what exists
    local cargo_omk="${CARGO_HOME:-$HOME/.cargo}/bin/omk"
    local found_anything=0

    if [[ -f "$cargo_omk" ]]; then
        found_anything=1
    fi

    local npm_omk=""
    if command -v npm &>/dev/null; then
        local npm_global_bin=""
        npm_global_bin="$(npm prefix -g 2>/dev/null)/bin" || true
        if [[ -n "$npm_global_bin" && -f "$npm_global_bin/omk" ]]; then
            npm_omk="$npm_global_bin/omk"
            found_anything=1
        fi
    fi

    if [[ "$found_anything" -eq 0 ]]; then
        echo -e "${GREEN}No legacy omk installations found.${NC}"
        echo -e "  ${GRAY}→${NC}  Nothing to clean up."
        exit 0
    fi

    # Show what will be removed
    echo -e "${YELLOW}Found legacy installations:${NC}"
    if [[ -f "$cargo_omk" ]]; then
        echo "  • $cargo_omk (cargo install)"
    fi
    if [[ -n "$npm_omk" ]]; then
        echo "  • $npm_omk (npm install -g)"
    fi
    echo ""

    # Confirmation
    if [[ "$FORCE" -eq 0 && "$DRY_RUN" -eq 0 ]]; then
        read -rp "Remove these files? [y/N] " confirm
        if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
            echo -e "\n${YELLOW}Cleanup cancelled.${NC}"
            exit 0
        fi
        echo ""
    fi

    # Perform cleanup
    echo -e "${BLUE}Cleaning up legacy installations...${NC}"
    echo ""

    if [[ -f "$cargo_omk" ]]; then
        cleanup_cargo
    fi

    if [[ -n "$npm_omk" ]]; then
        cleanup_npm
    fi

    echo ""
    if [[ "$DRY_RUN" -eq 1 ]]; then
        echo -e "${YELLOW}Dry run complete. No changes were made.${NC}"
    else
        echo -e "${GREEN}Legacy cleanup complete.${NC}"
    fi
}

main "$@"
