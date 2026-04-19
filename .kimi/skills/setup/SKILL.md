---
name: setup
description: Install or refresh OMK components
triggers:
  - "setup omk"
  - "omk setup"
  - "install omk"
---

# Setup

Install or refresh OMK components.

## Steps

1. **Check existing installation**: List `~/.kimi/skills/` for OMK skills
2. **Run installer**: Execute `./install.sh` from the OMK repository
3. **Verify agents**: Check that agent YAML files are in place
4. **Test state manager**: Run `python3 -m omk.state list`
5. **Report status**: Confirm installation is complete

## Tool Usage

- Use `Shell` to run install.sh
- Use `ReadFile` to verify configs
- Use `Glob` to check skill installation
