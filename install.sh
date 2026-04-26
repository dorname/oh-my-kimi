#!/usr/bin/env bash
#
# OMK Installer
# Installs all OMK skills and agent configs to Kimi CLI's skill directory.
#
# Usage:
#   ./install.sh              # Install to ~/.kimi/skills/
#   ./install.sh --project    # Install to ./.kimi/skills/ (project-local)
#   ./install.sh --target-dir /path/to/project  # Install to a specific project directory
#   ./install.sh --force      # Overwrite existing skills
#   ./install.sh --dry-run    # Show what would be installed

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FORCE=0
DRY_RUN=0
PROJECT_LOCAL=0
TARGET_DIR=""
NO_PIP=0
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
OMK Installer

Usage: $0 [OPTIONS]

Options:
  --project          Install skills to project-local .kimi/skills/ instead of ~/.kimi/skills/
  --target-dir DIR   Install skills to a specific project directory (DIR/.kimi/skills/)
  --force            Overwrite existing skills without prompting
  --dry-run          Show what would be installed without making changes
  --no-pip           Skip installing the omk Python package to the global environment
  --help             Show this help message

Examples:
  $0                          # Install globally (skills + omk CLI)
  $0 --project                # Install locally for current project
  $0 --target-dir ~/my-app    # Install to ~/my-app/.kimi/skills/
  $0 --force                  # Reinstall, overwriting existing skills
  $0 --no-pip                 # Install only skills, skip omk CLI package
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
            --force)
                FORCE=1
                shift
                ;;
            --dry-run)
                DRY_RUN=1
                shift
                ;;
            --no-pip)
                NO_PIP=1
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

get_target_agent_file() {
    local target_agents_dir
    target_agents_dir="$(get_target_agents_dir)"
    echo "$target_agents_dir/agent.yaml"
}

count_skills() {
    local count=0
    for skill_dir in "$SCRIPT_DIR"/skills/*/; do
        if [[ -f "$skill_dir/SKILL.md" ]]; then
            ((count++))
        fi
    done
    echo "$count"
}

install_skill() {
    local src="$1"
    local name="$2"
    local target="$3"
    local target_skill="$target/$name"

    if [[ -d "$target_skill" && "$FORCE" -eq 0 ]]; then
        echo -e "  ${YELLOW}⚠${NC}  $name (already exists, use --force to overwrite)"
        return 0
    fi

    if [[ "$DRY_RUN" -eq 1 ]]; then
        echo -e "  ${GRAY}→${NC}  $name"
        return 0
    fi

    mkdir -p "$target"

    if [[ -d "$target_skill" ]]; then
        rm -rf "$target_skill"
    fi

    cp -r "$src" "$target_skill"
    echo -e "  ${GREEN}✓${NC}  $name"
}

install_agents() {
    local target_agents
    target_agents="$(get_target_agents_dir)"

    mkdir -p "$target_agents"

    if [[ -d "$SCRIPT_DIR/agents" ]]; then
        if [[ "$DRY_RUN" -eq 1 ]]; then
            echo -e "\n${BLUE}Would install agents to:${NC} $target_agents"
        fi
        # Copy agent configs (explicit roster)
        for agent_file in "${public_agents[@]}"; do
            local src="$SCRIPT_DIR/agents/default/$agent_file"
            if [[ -f "$src" ]]; then
                if [[ "$DRY_RUN" -eq 1 ]]; then
                    echo -e "  ${GRAY}→${NC}  $agent_file"
                else
                    cp "$src" "$target_agents/"
                fi
            fi
        done
        if [[ "$DRY_RUN" -ne 1 ]]; then
            echo -e "\n${GREEN}✓${NC} Agent configs installed"
        fi
    fi
}

main() {
    parse_args "$@"

    echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║         OMK Installer                                    ║${NC}"
    echo -e "${BLUE}║   Kimi Orchestration & Multi-agent Coordination           ║${NC}"
    echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
    echo ""

    target_dir="$(get_target_dir)"

    if [[ "$DRY_RUN" -eq 1 ]]; then
        echo -e "${YELLOW}DRY RUN — no changes will be made${NC}\n"
    fi

    echo -e "${BLUE}Target directory:${NC} $target_dir"
    echo -e "${BLUE}Agent directory:${NC} $(get_target_agents_dir)"
    echo -e "${BLUE}Source directory:${NC} $SCRIPT_DIR/skills"
    echo ""

    # Validate source
    if [[ ! -d "$SCRIPT_DIR/skills" ]]; then
        echo -e "${RED}Error: Skills directory not found at $SCRIPT_DIR/skills${NC}"
        exit 1
    fi

    local skill_count
    skill_count="$(count_skills)"

    echo -e "${BLUE}Installing $skill_count skills...${NC}"
    echo ""

    for skill_dir in "$SCRIPT_DIR"/skills/*/; do
        if [[ -f "$skill_dir/SKILL.md" ]]; then
            local name
            name="$(basename "$skill_dir")"
            install_skill "$skill_dir" "$name" "$target_dir"
        fi
    done

    # Install agent configs
    install_agents

    # Install omk Python package globally if a package manager is available
    if [[ "$NO_PIP" -eq 0 && "$DRY_RUN" -eq 0 ]]; then
        local pkg_mgr=""
        local install_cmd=""
        if command -v pip3 &>/dev/null || command -v pip &>/dev/null; then
            pkg_mgr="pip"
            install_cmd="$(command -v pip3 || command -v pip) install -q -e '$SCRIPT_DIR'"
        elif command -v uv &>/dev/null; then
            pkg_mgr="uv"
            install_cmd="uv pip install --system -q -e '$SCRIPT_DIR'"
        fi

        if [[ -n "$pkg_mgr" ]]; then
            echo ""
            echo -e "${BLUE}Installing omk Python package via ${pkg_mgr}...${NC}"
            if eval "$install_cmd" 2>/dev/null; then
                echo -e "  ${GREEN}✓${NC}  omk CLI installed globally"
                echo -e "  ${GRAY}→${NC}  Run 'omk --help' to verify"
            else
                echo -e "  ${YELLOW}⚠${NC}  ${pkg_mgr} install failed (try: pip install -e .)"
            fi
        else
            echo ""
            echo -e "${YELLOW}Neither pip nor uv found — skipping omk CLI package install${NC}"
            echo -e "  ${GRAY}→${NC}  Install Python + pip (or uv), then run: pip install -e ."
        fi
    elif [[ "$DRY_RUN" -eq 1 && "$NO_PIP" -eq 0 ]]; then
        echo ""
        echo -e "${GRAY}→${NC}  Would install omk Python package (pip install -e $SCRIPT_DIR)"
    fi

    echo ""

    if [[ "$DRY_RUN" -eq 1 ]]; then
        echo -e "${YELLOW}Dry run complete. No changes were made.${NC}"
        echo -e "Run without ${GRAY}--dry-run${NC} to install."
    else
        echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
        echo -e "${GREEN}║         Installation Complete!                            ║${NC}"
        echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
        echo ""
        echo -e "${BLUE}Installed skills:${NC} $skill_count"
        echo -e "${BLUE}Location:${NC} $target_dir"
        echo -e "${BLUE}Agent file:${NC} $(get_target_agent_file)"
        echo ""
        echo -e "${YELLOW}Usage:${NC}"
        echo "  Launch Kimi with the OMK custom root agent:"
        echo "    kimi --agent-file \"$(get_target_agent_file)\""
        echo ""
        echo "  Then use OMK skills naturally inside that session:"
        echo "    autopilot: build a REST API"
        echo "    ralph: refactor the auth module"
        echo "    plan this feature"
        echo ""
        echo -e "${YELLOW}Next steps:${NC}"
        echo "  1. Ensure Kimi CLI is installed and configured"
        echo "  2. Start Kimi with the --agent-file command shown above"
        echo "  3. OMK skills in the installed skills directory will auto-detect based on your prompts"
        echo ""
        echo -e "${YELLOW}Compatibility note:${NC}"
        echo "  Plain 'kimi' does not load the OMK custom root agent by default."
    fi
}

main "$@"
