#!/usr/bin/env bash
#
# OMK LSP Diagnostics Wrapper
# Provides IDE-like diagnostics via standard CLI tools.
#
# Usage:
#   ./lsp-diagnostics.sh [file|directory]
#   ./lsp-diagnostics.sh --project
#   ./lsp-diagnostics.sh --typecheck
#   ./lsp-diagnostics.sh --symbols <file>
#   ./lsp-diagnostics.sh --references <symbol>

set -euo pipefail

show_help() {
    cat <<EOF
OMK LSP Diagnostics Wrapper

Usage: $0 [OPTIONS] [PATH]

Commands:
  (default)          Run all available diagnostics on PATH (default: .)
  --project          Run project-wide diagnostics
  --typecheck        Run TypeScript type checking only
  --lint             Run linting only
  --format-check     Check formatting only
  --symbols <file>   List symbols in a file
  --references <sym> Find references to a symbol
  --help             Show this help

Examples:
  $0 src/utils.ts           # Check specific file
  $0 --project             # Full project check
  $0 --typecheck           # TypeScript only
EOF
}

run_typecheck() {
    local target="${1:-.}"
    if [[ -f "tsconfig.json" ]]; then
        echo "=== TypeScript Type Check ==="
        if command -v npx &>/dev/null; then
            npx tsc --noEmit 2>&1 || true
        else
            echo "Warning: npx not found, skipping TypeScript check"
        fi
    fi
}

run_lint() {
    local target="${1:-.}"
    echo "=== Lint Check ==="
    if [[ -f "eslint.config.js" ]] || [[ -f ".eslintrc.json" ]] || [[ -f ".eslintrc.js" ]]; then
        if command -v npx &>/dev/null; then
            npx eslint "${target}" 2>&1 || true
        else
            echo "Warning: npx not found, skipping ESLint"
        fi
    elif [[ -f "pyproject.toml" ]] || [[ -f "setup.cfg" ]] || [[ -f ".flake8" ]]; then
        if command -v flake8 &>/dev/null; then
            flake8 "${target}" 2>&1 || true
        else
            echo "Warning: flake8 not found"
        fi
    elif [[ -f "Cargo.toml" ]]; then
        if command -v cargo &>/dev/null; then
            cargo clippy 2>&1 || true
        else
            echo "Warning: cargo not found"
        fi
    else
        echo "No recognized linter config found"
    fi
}

run_format_check() {
    echo "=== Format Check ==="
    if [[ -f ".prettierrc" ]] || [[ -f ".prettierrc.json" ]]; then
        if command -v npx &>/dev/null; then
            npx prettier --check . 2>&1 || true
        fi
    elif [[ -f "pyproject.toml" ]]; then
        if command -v black &>/dev/null; then
            black --check . 2>&1 || true
        fi
    elif [[ -f "rustfmt.toml" ]]; then
        if command -v cargo &>/dev/null; then
            cargo fmt -- --check 2>&1 || true
        fi
    fi
}

list_symbols() {
    local file="$1"
    if [[ ! -f "$file" ]]; then
        echo "Error: File not found: $file"
        exit 1
    fi
    echo "=== Symbols in $file ==="
    # Use ctags if available, otherwise grep for common patterns
    if command -v ctags &>/dev/null; then
        ctags -x --sort=no "$file" 2>/dev/null || true
    else
        # Fallback: grep for function/class definitions
        case "$file" in
            *.py)
                grep -nE '^(def |class )' "$file" || true
                ;;
            *.ts|*.js|*.tsx|*.jsx)
                grep -nE '^(export )?(async )?(function|class|const |let |var |interface |type )' "$file" || true
                ;;
            *.rs)
                grep -nE '^(fn |struct |enum |impl |trait |pub )' "$file" || true
                ;;
            *.go)
                grep -nE '^(func |type |var |const )' "$file" || true
                ;;
            *)
                grep -nE '^(function|def |class |fn )' "$file" || true
                ;;
        esac
    fi
}

find_references() {
    local symbol="$1"
    echo "=== References to '$symbol' ==="
    if command -v rg &>/dev/null; then
        rg --line-number --with-filename "\\b${symbol}\\b" . 2>/dev/null | head -50 || true
    elif command -v grep &>/dev/null; then
        grep -rn "\\b${symbol}\\b" . 2>/dev/null | head -50 || true
    else
        echo "Error: No search tool found (install ripgrep or grep)"
        exit 1
    fi
}

main() {
    local cmd=""
    local target="."

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --help|-h)
                show_help
                exit 0
                ;;
            --project)
                cmd="project"
                shift
                ;;
            --typecheck)
                cmd="typecheck"
                shift
                ;;
            --lint)
                cmd="lint"
                shift
                ;;
            --format-check)
                cmd="format"
                shift
                ;;
            --symbols)
                cmd="symbols"
                shift
                target="${1:-}"
                shift
                ;;
            --references)
                cmd="references"
                shift
                target="${1:-}"
                shift
                ;;
            -*)
                echo "Unknown option: $1"
                show_help
                exit 1
                ;;
            *)
                target="$1"
                shift
                ;;
        esac
    done

    case "$cmd" in
        symbols)
            list_symbols "$target"
            ;;
        references)
            find_references "$target"
            ;;
        typecheck)
            run_typecheck "$target"
            ;;
        lint)
            run_lint "$target"
            ;;
        format)
            run_format_check
            ;;
        project|"")
            run_typecheck "$target"
            run_lint "$target"
            run_format_check
            ;;
    esac
}

main "$@"
