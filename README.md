# OMK (Kimi Orchestration & Multi-agent Coordination)

> Oh-My-Kimi. Multi-agent orchestration for Kimi CLI.. Multi-agent orchestration, workflow skills, and stateful execution — now on Kimi.

## Overview

OMK ports the full OMC multi-agent orchestration experience to [Kimi Code CLI](https://github.com/MoonshotAI/kimi-cli). It provides:

- **35+ workflow skills** — autopilot, ralph, ultrawork, team, plan, and more
- **19 specialized agents** — architect, executor, debugger, critic, designer, etc.
- **Unified state management** — persistent plans, notepads, project memory, and wikis
- **Zero Claude dependency** — runs entirely on Kimi CLI's native toolset

## Quick Start

```bash
# 1. Clone or download this repository
git clone https://github.com/your-org/oh-my-kimi.git
cd oh-my-kimi

# 2. Install skills to Kimi CLI
./install.sh

# 3. Start using skills in any Kimi CLI session
# (skills auto-detect via keywords or use natural language)
```

## Architecture

```
User Input → Skill Detection → Agent Orchestration → Tools & State
                │                    │
                ▼                    ▼
         .kimi/skills/         Agent YAML configs
         (35+ SKILL.md)        (19 subagents)
                │                    │
                └────────┬───────────┘
                         ▼
                  .omk/state/
              (JSON/Markdown files)
```

## Core Skills

| Skill | Trigger | Description |
|-------|---------|-------------|
| `autopilot` | "autopilot", "build me" | Full autonomous execution from idea to working code |
| `ralph` | "ralph", "don't stop" | Self-referential persistence loop until completion |
| `ultrawork` | "ultrawork", "parallel" | Parallel execution engine |
| `team` | "team" | N coordinated agents on shared task list |
| `plan` | "plan this" | Strategic planning with optional interview |
| `deep-interview` | "deep interview" | Socratic requirements gathering |
| `ultraqa` | "ultraqa" | QA cycling: test, verify, fix, repeat |

See `skills/` for the complete catalog.

## Agent Catalog

| Agent | Role | When to Use |
|-------|------|-------------|
| `architect` | System design, debugging | Architecture, interfaces, trade-offs |
| `executor` | Implementation | Coding, refactoring, feature work |
| `explore` | Codebase search | Finding files, symbols, patterns |
| `debugger` | Root-cause analysis | Build errors, regressions, failures |
| `critic` | Plan review | Gap analysis, design validation |
| `designer` | UI/UX | Components, styling, interaction |
| `writer` | Documentation | Docs, migration notes, guides |
| `security-reviewer` | Security audit | Vulnerabilities, trust boundaries |
| `code-reviewer` | Quality review | Logic, maintainability, anti-patterns |

See `agents/` for all 19 agent configurations.

## State & Memory

OMK stores all state in your project directory under `.omk/`:

| Path | Purpose |
|------|---------|
| `.omk/state/` | Mode state files (JSON) |
| `.omk/notepad.md` | Session-persistent notes |
| `.omk/project-memory.json` | Cross-session project knowledge |
| `.omk/plans/` | Planning documents |
| `.omk/wiki/` | Markdown knowledge base |
| `.omk/logs/` | Audit logs |

## Differences from OMC

| Feature | OMC (Claude Code) | OMK (Kimi CLI) |
|---------|-------------------|-----------------|
| Agent system | Claude Agent SDK `Task()` | Kimi CLI `Agent()` |
| Model routing | haiku/sonnet/opus | Prompt-based guidance |
| Hooks | Shell hooks on lifecycle events | Skill triggers + AGENTS.md |
| Team workers | tmux + Claude CLI processes | Native Agent parallel calls |
| MCP servers | In-process MCP | Shell CLI wrappers / built-in tools |
| HUD | Stdin statusline | Not supported |
| Notifications | Hook-driven | Shell curl scripts |

## Contributing

1. Skills live in `skills/<name>/SKILL.md`
2. Agents live in `agents/default/<name>.yaml`
3. Scripts live in `scripts/`
4. Follow the [skill creator guide](https://moonshotai.github.io/kimi-cli/zh/customization/skills.html) for SKILL.md format

## License

MIT
