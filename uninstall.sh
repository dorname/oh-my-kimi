#!/usr/bin/env bash
#
# OMK Uninstaller
# Removes OMK skills, agent configs, Python package, and runtime state.
#
# Usage:
#   ./uninstall.sh              # Uninstall from ~/.kimi/skills/
#   ./uninstall.sh --project    # Uninstall from ./.kimi/skills/ (project-local)
#   ./uninstall.sh --target-dir /path/to/project  # Uninstall from a specific project
#   ./uninstall.sh --keep-state # Keep the .omk/ runtime state directory
#   ./uninstall.sh --dry-run    # Show what would be removed
#   ./uninstall.sh --force      # Skip confirmation prompt

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FORCE=0
DRY_RUN=0
PROJECT_LOCAL=0
TARGET_DIR=""
KEEP_STATE=0
# Public agent roster (18 agents + root configs)
public_agents=(
    "agent.yaml"
    "system.md"
    "coder.yaml"
    "explore.yaml"
    "plan.yaml"
    "architect.yaml"
    "executor.yaml"
    "debugger.yaml"
    "critic.yaml"
    "analyst.yaml"
    "designer.yaml"
    "writer.yaml"
    "verifier.yaml"
    "tracer.yaml"
    "code-reviewer.yaml"
    "security-reviewer.yaml"
    "test-engineer.yaml"
    "document-specialist.yaml"
    "code-simplifier.yaml"
    "scientist.yaml"
)

# Non-public agent files that must NOT be installed
non_public_agents=(
    "git-master.yaml"
    "qa-tester.yaml"
)

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
GRAY='\033[0;90m'
NC='\033[0m' # No Color

usage() {
    cat <<EOF
OMK Uninstaller

Usage: $0 [OPTIONS]

Options:
  --project          Uninstall from project-local .kimi/skills/ instead of ~/.kimi/skills/
  --target-dir DIR   Uninstall from a specific project directory (DIR/.kimi/skills/)
  --keep-state       Keep the .omk/ runtime state directory
  --force            Skip confirmation prompt
  --dry-run          Show what would be removed without making changes
  --help             Show this help message

Examples:
  $0                          # Uninstall globally (skills + omk CLI)
  $0 --project                # Uninstall locally for current project
  $0 --target-dir ~/my-app    # Uninstall from ~/my-app/.kimi/skills/
  $0 --keep-state             # Uninstall but preserve .omk/ state
  $0 --force                  # Uninstall without confirmation
EOF
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --project)
                PROJECT_LOCAL=1
                shift
                ;;
            --target-dir)
                if [[ -z "${2:-}" ]]; then
                    echo -e "${RED}Error: --target-dir requires a directory argument${NC}"
                    usage
                    exit 1
                fi
                TARGET_DIR="$2"
                shift 2
                ;;
            --keep-state)
                KEEP_STATE=1
                shift
                ;;
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

get_target_dir() {
    if [[ -n "$TARGET_DIR" ]]; then
        echo "$TARGET_DIR/.kimi/skills"
    elif [[ "$PROJECT_LOCAL" -eq 1 ]]; then
        echo "$SCRIPT_DIR/.kimi/skills"
    else
        # Check for XDG_CONFIG_HOME first, then fall back to home
        if [[ -n "${XDG_CONFIG_HOME:-}" ]]; then
            echo "$XDG_CONFIG_HOME/kimi/skills"
        else
            echo "$HOME/.kimi/skills"
        fi
    fi
}

get_target_agents_dir() {
    local target_dir
    target_dir="$(get_target_dir)"
    echo "$(dirname "$target_dir")/agents"
}

get_omk_dir() {
    if [[ "$PROJECT_LOCAL" -eq 1 ]]; then
        echo "$SCRIPT_DIR/.omk"
    elif [[ -n "$TARGET_DIR" ]]; then
        echo "$TARGET_DIR/.omk"
    else
        # For global uninstall, .omk/ is in the current working directory
        # because state is project-local, not global
        echo ""
    fi
}

count_skills() {
    local count=0
    for skill_dir in "$SCRIPT_DIR"/skills/*/; do
        if [[ -f "$skill_dir/SKILL.md" ]]; then
            count=$((count + 1))
        fi
    done
    echo "$count"
}

uninstall_skill() {
    local name="$1"
    local target="$2"
    local target_skill="$target/$name"

    if [[ ! -d "$target_skill" ]]; then
        return 0
    fi

    if [[ "$DRY_RUN" -eq 1 ]]; then
        echo -e "  ${GRAY}→${NC}  $name"
        return 0
    fi

    rm -rf "$target_skill"
    echo -e "  ${GREEN}✓${NC}  Removed $name"
}

uninstall_agents() {
    local target_agents
    target_agents="$(get_target_agents_dir)"

    if [[ ! -d "$target_agents" ]]; then
        return 0
    fi

    local removed=0
    for agent_file in "${public_agents[@]}"; do
        local target_file="$target_agents/$agent_file"
        if [[ -f "$target_file" ]]; then
            if [[ "$DRY_RUN" -eq 1 ]]; then
                echo -e "  ${GRAY}→${NC}  $agent_file"
            else
                rm -f "$target_file"
                echo -e "  ${GREEN}✓${NC}  Removed $agent_file"
            fi
            removed=$((removed + 1))
        fi
    done

    if [[ "$DRY_RUN" -eq 1 && "$removed" -gt 0 ]]; then
        echo -e "\n${BLUE}Would remove agents from:${NC} $target_agents"
    elif [[ "$removed" -gt 0 ]]; then
        echo -e "\n${GREEN}✓${NC} Agent configs removed"
    fi
}

uninstall_pip_package() {
    if [[ "$DRY_RUN" -eq 1 ]]; then
        echo -e "  ${GRAY}→${NC}  Would uninstall omk Python package"
        return 0
    fi

    local uninstalled=0
    if command -v pip3 &>/dev/null || command -v pip &>/dev/null; then
        local pip_cmd
        pip_cmd="$(command -v pip3 || command -v pip)"
        if $pip_cmd show omk &>/dev/null; then
            $pip_cmd uninstall -y omk &>/dev/null || true
            echo -e "  ${GREEN}✓${NC}  Uninstalled omk via pip"
            uninstalled=1
        fi
    fi

    if command -v uv &>/dev/null; then
        if uv pip show omk &>/dev/null 2>&1; then
            uv pip uninstall omk &>/dev/null || true
            echo -e "  ${GREEN}✓${NC}  Uninstalled omk via uv"
            uninstalled=1
        fi
    fi

    if [[ "$uninstalled" -eq 0 ]]; then
        echo -e "  ${YELLOW}⚠${NC}  omk Python package not found (may have been manually uninstalled)"
    fi
}

uninstall_omk_state() {
    local omk_dir
    omk_dir="$(get_omk_dir)"

    if [[ -z "$omk_dir" ]]; then
        # Global uninstall: .omk/ is project-local, skip
        return 0
    fi

    if [[ ! -d "$omk_dir" ]]; then
        return 0
    fi

    if [[ "$DRY_RUN" -eq 1 ]]; then
        echo -e "  ${GRAY}→${NC}  Would remove $omk_dir/"
        return 0
    fi

    rm -rf "$omk_dir"
    echo -e "  ${GREEN}✓${NC}  Removed $omk_dir/"
}

main() {
    parse_args "$@"

    echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║         OMK Uninstaller                                  ║${NC}"
    echo -e "${BLUE}║   Kimi Orchestration & Multi-agent Coordination           ║${NC}"
    echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
    echo ""

    local target_dir
    target_dir="$(get_target_dir)"
    local target_agents
    target_agents="$(get_target_agents_dir)"
    local omk_dir
    omk_dir="$(get_omk_dir)"

    if [[ "$DRY_RUN" -eq 1 ]]; then
        echo -e "${YELLOW}DRY RUN — no changes will be made${NC}\n"
    fi

    echo -e "${BLUE}Target skills directory:${NC} $target_dir"
    echo -e "${BLUE}Target agents directory:${NC} $target_agents"
    if [[ -n "$omk_dir" ]]; then
        echo -e "${BLUE}Runtime state directory:${NC} $omk_dir/"
    fi
    echo ""

    # Check if anything is actually installed
    local found_anything=0
    if [[ -d "$target_dir" ]]; then
        for skill_dir in "$SCRIPT_DIR"/skills/*/; do
            if [[ -f "$skill_dir/SKILL.md" ]]; then
                local name
                name="$(basename "$skill_dir")"
                if [[ -d "$target_dir/$name" ]]; then
                    found_anything=1
                    break
                fi
            fi
        done
    fi

    if [[ "$found_anything" -eq 0 && "$DRY_RUN" -eq 0 ]]; then
        echo -e "${YELLOW}No OMK skills found in target directory.${NC}"
        echo -e "  ${GRAY}→${NC}  Already uninstalled or installed elsewhere?"
        echo ""
    fi

    # Confirmation
    if [[ "$FORCE" -eq 0 && "$DRY_RUN" -eq 0 ]]; then
        echo -e "${YELLOW}This will remove:${NC}"
        echo "  • OMK skills from $target_dir"
        echo "  • OMK agent configs from $target_agents"
        echo "  • The omk Python package"
        if [[ -n "$omk_dir" && "$KEEP_STATE" -eq 0 ]]; then
            echo "  • Runtime state from $omk_dir/"
        fi
        echo ""
        read -rp "Are you sure? [y/N] " confirm
        if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
            echo -e "\n${YELLOW}Uninstall cancelled.${NC}"
            exit 0
        fi
        echo ""
    fi

    local skill_count
    skill_count="$(count_skills)"

    # Uninstall skills
    echo -e "${BLUE}Removing $skill_count OMK skills...${NC}"
    echo ""
    for skill_dir in "$SCRIPT_DIR"/skills/*/; do
        if [[ -f "$skill_dir/SKILL.md" ]]; then
            local name
            name="$(basename "$skill_dir")"
            uninstall_skill "$name" "$target_dir"
        fi
    done

    # Uninstall agent configs
    echo ""
    echo -e "${BLUE}Removing OMK agent configs...${NC}"
    uninstall_agents

    # Uninstall Python package
    echo ""
    echo -e "${BLUE}Removing omk Python package...${NC}"
    uninstall_pip_package

    # Remove runtime state
    if [[ -n "$omk_dir" && "$KEEP_STATE" -eq 0 ]]; then
        echo ""
        echo -e "${BLUE}Removing runtime state...${NC}"
        uninstall_omk_state
    elif [[ -n "$omk_dir" && "$KEEP_STATE" -eq 1 ]]; then
        echo ""
        echo -e "${YELLOW}--keep-state specified; preserving $omk_dir/${NC}"
    fi

    # Clean up empty directories
    local cleaned_dirs=()
    if [[ -d "$target_dir" && -z "$(ls -A "$target_dir" 2>/dev/null)" ]]; then
        if [[ "$DRY_RUN" -eq 0 ]]; then
            rmdir "$target_dir"
            cleaned_dirs+=("$target_dir")
        fi
    fi
    if [[ -d "$target_agents" && -z "$(ls -A "$target_agents" 2>/dev/null)" ]]; then
        if [[ "$DRY_RUN" -eq 0 ]]; then
            rmdir "$target_agents"
            cleaned_dirs+=("$target_agents")
        fi
    fi
    # Clean up empty .kimi/ directory in project-local mode
    if [[ "$PROJECT_LOCAL" -eq 1 || -n "$TARGET_DIR" ]]; then
        local kimi_parent
        kimi_parent="$(dirname "$target_dir")"
        if [[ -d "$kimi_parent" && -z "$(ls -A "$kimi_parent" 2>/dev/null)" ]]; then
            if [[ "$DRY_RUN" -eq 0 ]]; then
                rmdir "$kimi_parent"
                cleaned_dirs+=("$kimi_parent")
            fi
        fi
    fi

    echo ""
    if [[ "$DRY_RUN" -eq 1 ]]; then
        echo -e "${YELLOW}Dry run complete. No changes were made.${NC}"
        echo -e "Run without ${GRAY}--dry-run${NC} to actually uninstall."
    else
        echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
        echo -e "${GREEN}║         Uninstall Complete!                               ║${NC}"
        echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
        echo ""
        echo -e "${YELLOW}What was removed:${NC}"
        echo "  • OMK skills from $target_dir"
        echo "  • OMK agent configs from $target_agents"
        echo "  • The omk Python package"
        if [[ -n "$omk_dir" && "$KEEP_STATE" -eq 0 ]]; then
            echo "  • Runtime state from $omk_dir/"
        fi
        if [[ ${#cleaned_dirs[@]} -gt 0 ]]; then
            echo "  • Empty directories cleaned up"
            for d in "${cleaned_dirs[@]}"; do
                echo "    - $d/"
            done
        fi
        echo ""
        echo -e "${YELLOW}Note:${NC}"
        echo "  To reinstall, run: ./install.sh"
    fi
}

main "$@"
