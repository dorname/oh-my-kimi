---
name: skill
description: Manage local skills — list, add, remove, search, edit, setup wizard
metadata:
  triggers:
  - skill
  - skills
  - manage skills
---

# Skill Manager

Manage local OMK/Kimi CLI skills.

## Commands

| Command | Action |
|---------|--------|
| `skill list` | List all installed skills |
| `skill search <query>` | Search skills by name or description |
| `skill add <name>` | Create a new skill from template |
| `skill edit <name>` | Edit an existing skill |
| `skill remove <name>` | Remove a skill |

## Steps

1. **Parse command**: Identify which skill management action
2. **Execute**:
   - List: inspect the active Kimi-discovered skills directory (`./.kimi/skills/`, `$XDG_CONFIG_HOME/kimi/skills/`, or `~/.kimi/skills/`) and read SKILL.md frontmatter
   - Search: `Grep` through skill directories
   - Add: Create directory + write template SKILL.md
   - Edit: `ReadFile` then `WriteFile`
   - Remove: Confirm then `rm -rf`

## Tool Usage

- Use `Shell` for directory operations
- Use `ReadFile` and `WriteFile` for skill content
- Use `Glob` and `Grep` for search
