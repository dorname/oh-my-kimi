# OMK Agent Guide

> Oh-My-Kimi (OMK) — Multi-agent orchestration for Kimi Code CLI.

## Project Structure

```
agents/default/      # Root agent + 18 public specialist subagents
skills/              # 36 skills (SKILL.md)
omk/                 # Python utilities (state, notifications, updater)
scripts/             # Shell-based integrations (notify, ast-search, etc.)
kimi-cli-docs/       # VitePress documentation site (not part of runtime)
```

## Skill Development Rules

### SKILL.md Format

All skills **must** follow the [Agent Skills open format](https://agentskills.io/):

```markdown
---
name: skill-name
description: One-line description of what this skill does
---

# Skill Title

## Use When
- Clear activation criteria

## Do Not Use When
- Counter-indications

## Workflow
1. Step-by-step instructions for the agent
```

**Frontmatter constraints (Kimi CLI enforced):**
- `name`: 1–64 chars, lowercase letters / numbers / hyphens only
- `description`: 1–1024 chars
- Custom fields (`triggers`, `user-invocable`, etc.) **must** live under `metadata`

**Content constraints:**
- Keep `SKILL.md` under 500 lines
- Use relative paths to reference `scripts/` or `references/` subdirectories
- Provide clear steps, input/output examples, and boundary cases

### Adding a New Skill

1. Create `skills/<name>/SKILL.md`
2. Add the skill's trigger words to `agents/default/system.md` in the OMK Skill Activation table
3. Add a one-line entry to `README.md` skill tables (both English and Chinese)
4. Run `scripts/check-agent-contract.py` to verify registry alignment

## Agent Configuration Rules

### YAML Format

All agent files use Kimi CLI's custom agent YAML format:

```yaml
version: 1
agent:
  extend: ./agent.yaml        # Subagents inherit the root agent
  system_prompt_args:
    ROLE_ADDITIONAL: |
      # Role-specific prompt text
```

**Subagent requirements:**
- Every subagent YAML **must** include `extend: ./agent.yaml`
- Subagents **must not** define `subagents:` (nesting is prohibited by Kimi CLI)
- Tool exclusions **must** block `Agent`, `AskUserQuestion`, `EnterPlanMode`, `ExitPlanMode` for non-coordinator roles

### Public Roster

The supported public subagent roster is 18 agents. Additional YAML files may exist, but only these are part of the documented public surface:

`coder`, `explore`, `plan`, `architect`, `executor`, `debugger`, `analyst`, `verifier`, `tracer`, `critic`, `code-reviewer`, `security-reviewer`, `test-engineer`, `designer`, `writer`, `document-specialist`, `code-simplifier`, `scientist`

## State & Conventions

- Runtime state lives in `.omk/state/<mode>-state.json`
- Plans live in `.omk/plans/`
- Wiki / memory live in `.omk/wiki/` and `.omk/project-memory.json`
- Use `ReadFile` / `WriteFile` for state; do not assume a database

## Coding Style

- Python: PEP 8, type hints where practical
- Shell: POSIX-compatible where possible; bashisms okay in `scripts/`
- Markdown: 80–100 char soft wrap for readability
- Keep changes minimal; follow existing patterns
