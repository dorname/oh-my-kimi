#!/usr/bin/env bash
#
# OMK AST Search Wrapper
# Wraps ast-grep for structural code search and replace.
#
# Usage:
#   ./ast-search.sh --search '<pattern>' [lang] [path]
#   ./ast-search.sh --replace '<pattern>' --by '<replacement>' [lang] [path]

set -euo pipefail

show_help() {
    cat <<EOF
OMK AST Search Wrapper

Usage: $0 [OPTIONS]

Options:
  --search <pattern>    Search for AST pattern
  --replace <pattern>   Pattern to replace
  --by <replacement>    Replacement text
  --lang <language>     Target language (ts, js, py, rs, go, etc.)
  --path <path>         Search path (default: .)
  --dry-run             Show replacements without applying
  --help                Show this help

Examples:
  $0 --search 'console.log($A)' --lang ts
  $0 --replace 'var $A = $B' --by 'const $A = $B' --lang js --dry-run
EOF
}

PATTERN=""
REPLACEMENT=""
BY=""
LANG=""
PATH="."
DRY_RUN=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        --help|-h)
            show_help
            exit 0
            ;;
        --search)
            PATTERN="$2"
            shift 2
            ;;
        --replace)
            REPLACEMENT="$2"
            shift 2
            ;;
        --by)
            BY="$2"
            shift 2
            ;;
        --lang)
            LANG="$2"
            shift 2
            ;;
        --path)
            PATH="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=1
            shift
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Check for ast-grep
if ! command -v ast-grep &>/dev/null && ! command -v sg &>/dev/null; then
    echo "Error: ast-grep not found. Install it with:"
    echo "  npm install -g @ast-grep/cli"
    echo "  or: cargo install ast-grep"
    exit 1
fi

SG_CMD="ast-grep"
if ! command -v ast-grep &>/dev/null; then
    SG_CMD="sg"
fi

# Build ast-grep command
ARGS=()

if [[ -n "$LANG" ]]; then
    ARGS+=("--lang" "$LANG")
fi

if [[ -n "$PATTERN" ]]; then
    ARGS+=("-p" "$PATTERN")
fi

if [[ -n "$REPLACEMENT" ]]; then
    ARGS+=("-p" "$REPLACEMENT")
fi

if [[ -n "$BY" ]]; then
    if [[ "$DRY_RUN" -eq 1 ]]; then
        ARGS+=("--rewrite" "$BY")
    else
        ARGS+=("--rewrite" "$BY" "-U")
    fi
fi

ARGS+=("$PATH")

echo "Running: $SG_CMD ${ARGS[*]}"
$SG_CMD "${ARGS[@]}"
