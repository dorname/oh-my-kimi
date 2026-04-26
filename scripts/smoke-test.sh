#!/usr/bin/env bash
#
# OMK Smoke Test — verify that agents and skills can be loaded after install.
#
# Usage:
#   ./scripts/smoke-test.sh           # project-local (default)
#   ./scripts/smoke-test.sh --global  # verify ~/.kimi/ installation
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
MODE="project"

usage() {
    echo "Usage: $0 [--global]"
    echo "  --global  Verify ~/.kimi/ installation instead of project-local"
}

if [[ "${1:-}" == "--global" ]]; then
    MODE="global"
elif [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
    usage
    exit 0
elif [[ -n "${1:-}" ]]; then
    echo "Unknown option: $1"
    usage
    exit 1
fi

if [[ "$MODE" == "project" ]]; then
    AGENTS_DIR="$PROJECT_DIR/.kimi/agents"
    SKILLS_DIR="$PROJECT_DIR/.kimi/skills"
else
    if [[ -n "${XDG_CONFIG_HOME:-}" ]]; then
        AGENTS_DIR="$XDG_CONFIG_HOME/kimi/agents"
        SKILLS_DIR="$XDG_CONFIG_HOME/kimi/skills"
    else
        AGENTS_DIR="$HOME/.kimi/agents"
        SKILLS_DIR="$HOME/.kimi/skills"
    fi
fi

ERRORS=0

echo "=== OMK Smoke Test ($MODE mode) ==="
echo ""

echo "--- 1. Agent YAML syntax check ---"
for f in "$PROJECT_DIR"/agents/default/*.yaml; do
    if python3 -c "import yaml; yaml.safe_load(open('$f'))" 2>/dev/null; then
        echo "  OK $(basename "$f")"
    else
        echo "  FAIL $(basename "$f"): invalid YAML"
        ((ERRORS++)) || true
    fi
done
echo ""

echo "--- 2. Agent configs installed ---"
if [[ ! -d "$AGENTS_DIR" ]]; then
    echo "  FAIL agents directory not found: $AGENTS_DIR"
    echo "       Run ./install.sh"$( [[ "$MODE" == "project" ]] && echo " --project" || echo "" )" first"
    ((ERRORS++)) || true
else
    # Verify public roster files exist
    PUBLIC_AGENTS=(
        agent.yaml system.md coder.yaml explore.yaml plan.yaml
        architect.yaml executor.yaml debugger.yaml critic.yaml
        analyst.yaml designer.yaml writer.yaml verifier.yaml
        tracer.yaml code-reviewer.yaml security-reviewer.yaml
        test-engineer.yaml document-specialist.yaml code-simplifier.yaml
        scientist.yaml
    )
    NON_PUBLIC_AGENTS=(git-master.yaml qa-tester.yaml)

    MISSING=0
    for f in "${PUBLIC_AGENTS[@]}"; do
        if [[ ! -f "$AGENTS_DIR/$f" ]]; then
            echo "  FAIL missing $f"
            ((MISSING++)) || true
        fi
    done

    EXTRA=0
    for f in "${NON_PUBLIC_AGENTS[@]}"; do
        if [[ -f "$AGENTS_DIR/$f" ]]; then
            echo "  WARN non-public file present: $f (from previous install)"
            ((EXTRA++)) || true
        fi
    done

    if [[ "$MISSING" -eq 0 ]]; then
        echo "  OK all 20 public agent files present"
    else
        echo "  FAIL $MISSING public agent file(s) missing"
        ((ERRORS++)) || true
    fi
fi
echo ""

echo "--- 3. Skills installed ---"
if [[ ! -d "$SKILLS_DIR" ]]; then
    echo "  FAIL skills directory not found: $SKILLS_DIR"
    ((ERRORS++)) || true
else
    SKILL_COUNT=0
    for f in "$SKILLS_DIR"/*/SKILL.md; do
        [[ -f "$f" ]] && ((SKILL_COUNT++)) || true
    done
    echo "  Skills found: $SKILL_COUNT"
    if [[ "$SKILL_COUNT" -eq 36 ]]; then
        echo "  OK expected 36"
    else
        echo "  FAIL expected 36, got $SKILL_COUNT"
        ((ERRORS++)) || true
    fi
fi
echo ""

echo "--- 4. Kimi CLI availability ---"
if command -v kimi &>/dev/null; then
    echo "  OK kimi CLI found"

    echo ""
    echo "--- 5. Agent load test ---"
    AGENT_FILE="$AGENTS_DIR/agent.yaml"
    if [[ -f "$AGENT_FILE" ]]; then
        # --help exits 0 even if agent loads successfully; we just care about no parse error
        if kimi --agent-file "$AGENT_FILE" --help >/dev/null 2>&1; then
            echo "  OK agent.yaml parsed by kimi"
        else
            # Some kimi versions may exit non-zero for --help; check stderr for parse errors
            if kimi --agent-file "$AGENT_FILE" --help 2>&1 | grep -qi "error\|invalid\|parse"; then
                echo "  FAIL agent.yaml failed to parse"
                ((ERRORS++)) || true
            else
                echo "  OK agent.yaml parsed by kimi (non-zero exit but no parse error)"
            fi
        fi
    else
        echo "  SKIP agent.yaml not installed"
    fi
else
    echo "  SKIP kimi CLI not in PATH"
fi

echo ""
if [[ "$ERRORS" -eq 0 ]]; then
    echo "=== Smoke test PASSED ==="
    exit 0
else
    echo "=== Smoke test FAILED ($ERRORS error(s)) ==="
    exit 1
fi
