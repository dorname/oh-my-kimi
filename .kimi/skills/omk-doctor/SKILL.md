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

1. **Skills directory**: Verify `~/.kimi/skills/` exists and contains OMK skills
2. **Agent configs**: Verify agent YAML files are valid
3. **State directory**: Verify `.omk/state/` is writable
4. **Dependencies**: Check for required tools (node, python, git, etc.)
5. **Environment**: Check OMK_* environment variables

## Steps

1. Run `ls ~/.kimi/skills/` to verify skill installation
2. Check agent configs with `cat ~/.kimi/skills/../agents/agent.yaml`
3. Test state manager: `python3 -m omk.state list`
4. Check dependencies: `which node python3 git`
5. Report findings and suggest fixes

## Tool Usage

- Use `Shell` for system checks
- Use `ReadFile` for config inspection
