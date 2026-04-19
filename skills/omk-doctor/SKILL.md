---
name: omk-doctor
description: Diagnose and fix OMK installation issues
triggers:
  - "doctor"
  - "omk doctor"
---

# OMK Doctor

Diagnose and fix OMK installation and configuration issues.

## Checks

1. **Skills directory**: Verify the active Kimi-discovered skills directory exists and contains OMK skills
2. **Agent configs**: Verify agent YAML files are valid
3. **State directory**: Verify `.omk/state/` is writable
4. **Dependencies**: Check for required tools (node, python, git, etc.)
5. **Environment**: Check OMK_* environment variables
6. **Install mode**: Detect whether OMK is installed project-locally, via `XDG_CONFIG_HOME`, or via `~/.kimi`

## Steps

1. Check supported install locations in order of likelihood:
   - project-local: `./.kimi/skills/`
   - XDG: `$XDG_CONFIG_HOME/kimi/skills/`
   - home: `~/.kimi/skills/`
2. Check the matching agent config alongside the detected skills directory:
   - `./.kimi/agents/agent.yaml`
   - `$XDG_CONFIG_HOME/kimi/agents/agent.yaml`
   - `~/.kimi/agents/agent.yaml`
3. Test state manager: `python3 -m omk.state list`
4. Check dependencies: `which node python3 git`
5. Report findings and suggest fixes

## Tool Usage

- Use `Shell` for system checks
- Use `ReadFile` for config inspection
