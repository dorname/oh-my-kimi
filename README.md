# OMK (Kimi Orchestration & Multi-agent Coordination)

> Oh-My-Kimi. Multi-agent orchestration for [Kimi Code CLI](https://github.com/MoonshotAI/kimi-cli). 35+ workflow skills, 18 public specialist agents, and stateful execution.

## Overview

OMK ports the full OMC multi-agent orchestration experience to Kimi CLI. It provides:

- **36 workflow skills** — autopilot, ralph, ultrawork, team, plan, deep-dive, and more
- **18 public specialist agents** — coder, plan, architect, executor, debugger, critic, verifier, and more
- **Unified state management** — persistent plans, notepads, project memory, and wikis
- **Notification integrations** — Telegram, Discord, Slack via shell scripts
- **Zero Claude dependency** — runs entirely on Kimi CLI's native toolset

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/your-org/oh-my-kimi.git
cd oh-my-kimi

# 2. Install skills and the omk CLI globally (default: ~/.kimi/skills/ + pip install -e .)
./install.sh

# 3. Or install project-locally
./install.sh --project

# 4. Or install to a specific project
./install.sh --target-dir ~/my-project

# 5. Or install only skills (skip the omk Python package)
./install.sh --no-pip

# 6. Launch OMK on Kimi CLI
# Global install (default when XDG_CONFIG_HOME is unset)
kimi --agent-file "$HOME/.kimi/agents/agent.yaml"

# If XDG_CONFIG_HOME is set
kimi --agent-file "$XDG_CONFIG_HOME/kimi/agents/agent.yaml"

# Project-local install (run from the project root)
kimi --agent-file ./.kimi/agents/agent.yaml

# 7. Verify the omk CLI is available globally
omk --help
omk state list
```

### Install Options

| Option | Description |
|--------|-------------|
| `--project` | Install to `./.kimi/skills/` (project-local) |
| `--target-dir DIR` | Install to `DIR/.kimi/skills/` |
| `--force` | Overwrite existing skills |
| `--dry-run` | Preview what would be installed |
| `--no-pip` | Skip installing the `omk` Python package globally |
| `--help` | Show full help |

### Compatibility Target

OMK's supported Kimi CLI `1.36.0` bootstrap contract is:

- Install skills into a Kimi-discovered skills directory such as `~/.kimi/skills/` or `./.kimi/skills/`.
- Launch Kimi with the OMK custom root agent via `--agent-file`.
- Treat plain `kimi` without `--agent-file` as vanilla Kimi, not OMK.

### First Use

Start Kimi with the OMK root agent, then use skills naturally via keywords:

```bash
kimi --agent-file ./.kimi/agents/agent.yaml

autopilot: build a REST API for user management
ralph: refactor the auth module until all tests pass
plan this feature with consensus mode
team 3:executor fix all TypeScript errors
deep dive into why the build is failing
ultraqa the login flow
```

## Architecture

```
User Input → kimi --agent-file .kimi/agents/agent.yaml → Skill Detection → Agent Orchestration → Tools & State
                                                           │                    │
                                                           ▼                    ▼
                                                    .kimi/skills/         Agent YAML configs
                                                    (35+ SKILL.md)        (18 public roles)
                                                           │                    │
                                                           └────────┬───────────┘
                                                                    ▼
                                                             .omk/state/
                                                         (JSON/Markdown files)
```

## Core Skills

### Workflow Skills

| Skill | Trigger | Description |
|-------|---------|-------------|
| `autopilot` | "autopilot", "build me", "I want a" | Full autonomous execution from idea to working code |
| `ralph` | "ralph", "don't stop", "must complete" | Self-referential persistence loop with PRD-driven verification |
| `ultrawork` | "ultrawork", "ulw", "parallel" | Maximum parallelism with parallel agent orchestration |
| `team` | "team" | N coordinated agents on shared task list |
| `plan` | "plan this", "plan the", "let's plan" | Strategic planning with optional interview |
| `ralplan` | "ralplan", "consensus plan" | Iterative consensus planning with deliberation |
| `deep-interview` | "deep interview", "interview me" | Socratic deep interview with ambiguity gating |
| `deep-dive` | "deep dive" | 2-stage pipeline: trace → deep-interview |
| `ultraqa` | "ultraqa" | QA cycling — test, verify, fix, repeat |
| `ai-slop-cleaner` | "cleanup", "deslop", "anti-slop" | Regression-safe cleanup workflow |
| `visual-verdict` | "visual verdict" | Structured visual QA for screenshot comparisons |
| `trace` | "trace" | Evidence-driven tracing with competing hypotheses |
| `ccg` | "ccg" | Claude-Codex-Gemini tri-model orchestration |
| `sciomk` | "sciomk" | Parallel scientist agents for comprehensive analysis |
| `self-improve` | "self-improve" | Autonomous evolutionary code improvement |

### Utilities

| Skill | Trigger | Description |
|-------|---------|-------------|
| `cancel` | "cancel", "stop", "abort" | Cancel active execution modes |
| `ask` | "ask" | Provider advisor routing (Claude, Codex, Gemini) |
| `setup` | "setup" | Install or refresh OMK components |
| `omk-doctor` | "doctor" | Diagnose installation issues |
| `verify` | "verify" | Verify that a change really works |
| `debug` | "debug" | Diagnose current session or repo state |
| `release` | "release" | Generic release assistant |
| `skill` | "skill" | Manage local skills |
| `skillify` | "skillify" | Turn a workflow into a skill draft |
| `configure-notifications` | "configure notifications" | Configure Telegram, Discord, Slack |
| `mcp-setup` | "mcp setup" | Configure external CLI tools (ast-grep, Playwright, etc.) |

### Memory & Knowledge

| Skill | Trigger | Description |
|-------|---------|-------------|
| `learner` | "learner" | Extract a learned skill from conversation |
| `wiki` | "wiki" | Persistent markdown knowledge base |
| `writer-memory` | "writer-memory" | Agentic memory for writers |
| `remember` | "remember" | Review reusable project knowledge |
| `omk-reference` | (auto-load) | Agent catalog, tools, pipeline routing |

See `skills/` for the complete catalog.

## Agent Catalog

Invoke via `Agent(subagent_type="<name>", ...)`.

### Build/Analysis Lane

| Agent | Description | When to Use |
|-------|-------------|-------------|
| `coder` | General software engineering tasks | Small or mixed implementation work |
| `explore` | Fast codebase search, file/symbol mapping | Quick lookups, finding files, understanding structure |
| `analyst` | Requirements clarity, acceptance criteria, hidden constraints | Broad requests, vague requirements |
| `plan` | Task sequencing, execution plans, risk flags | Before multi-file implementations |
| `architect` | System design, boundaries, interfaces, long-horizon tradeoffs | Complex refactors, new features |
| `debugger` | Root-cause analysis, regression isolation, failure diagnosis | Build errors, test failures, bugs |
| `executor` | Code implementation, refactoring, feature work | The default for coding tasks |
| `verifier` | Completion evidence, claim validation, test adequacy | Before claiming done |
| `tracer` | Evidence-driven tracing, competing hypotheses | Causal investigation |

### Review Lane

| Agent | Description | When to Use |
|-------|-------------|-------------|
| `code-reviewer` | Comprehensive review — logic, maintainability, anti-patterns | Pre-merge quality gate |
| `security-reviewer` | Vulnerabilities, trust boundaries, authn/authz | Security-critical changes |

### Domain Specialists

| Agent | Description | When to Use |
|-------|-------------|-------------|
| `test-engineer` | Test strategy, coverage, flaky-test hardening | Adding or improving tests |
| `designer` | UI/UX architecture, interaction design | Frontend work, styling |
| `writer` | Docs, migration notes, user guidance | Documentation tasks |
| `document-specialist` | External docs, API/SDK reference lookup | Unknown SDKs, frameworks |
| `code-simplifier` | Code clarity, simplification, maintainability | Cleanup, deslop passes |
| `scientist` | Data analysis, statistical research | Data-heavy tasks |

### Coordination

| Agent | Description | When to Use |
|-------|-------------|-------------|
| `critic` | Plan/design critical challenge | Before committing to plans |

Compatibility target for Kimi CLI `1.36.0`: the public OMK roster is the 18 agents listed above. Additional shipped YAML files are not part of the supported public surface unless they are wired into a documented workflow.

## OMK CLI & State Management

OMK includes a Python utility package (`omk/`) for state management and helpers:

```bash
# State management (global omk CLI or python3 -m)
omk state list                          # List active modes
omk state read ralph                    # Read ralph state
omk state write ralph '{"active":true}' # Write state
omk state clear ralph                   # Clear state

# Notifications
omk notifier telegram "Build complete"
omk notifier discord "Deployment done"

# Update check
omk updater

# Legacy module syntax still works
python3 -m omk.state list
python3 -m omk.notifier telegram "msg"
python3 -m omk.updater
```

OMK stores all runtime state in your project directory under `.omk/`:

| Path | Purpose |
|------|---------|
| `.omk/state/` | Mode state files (JSON) |
| `.omk/notepad.md` | Session-persistent notes |
| `.omk/project-memory.json` | Cross-session project knowledge |
| `.omk/plans/` | Planning documents |
| `.omk/wiki/` | Markdown knowledge base |
| `.omk/logs/` | Audit logs |

## Scripts & Integrations

The `scripts/` directory provides shell-based utilities:

| Script | Purpose |
|--------|---------|
| `notify.sh` | Send notifications to Telegram, Discord, Slack |
| `update-check.sh` | Check for OMK updates from GitHub releases |
| `ast-search.sh` | Structural code search via ast-grep |
| `lsp-diagnostics.sh` | Language server diagnostics wrapper |
| `rate-limit-wait.sh` | Rate limit handling helper |
| `check-agent-contract.py` | Verify that registry, docs, installer messaging, and skill role references stay aligned |

### Notification Setup

Configure via environment variables:

```bash
export OMK_TELEGRAM_TOKEN="your-bot-token"
export OMK_TELEGRAM_CHAT="your-chat-id"
export OMK_DISCORD_WEBHOOK="your-webhook-url"
export OMK_SLACK_WEBHOOK="your-webhook-url"
```

Or use the `configure-notifications` skill for guided setup.

## Extended Features

### Project Session Manager

Manage isolated git worktrees for parallel development:

```
"project session feat-auth-123"
"worktree for issue #456"
```

Sessions are tracked in `.omk/state/sessions/` with branch and worktree metadata.

### External Tool Setup

OMK can configure external CLI tools for enhanced agent capabilities:

| Tool | CLI | Use Case |
|------|-----|----------|
| ast-grep | `sg` | Structural code search |
| Playwright | `npx @playwright/mcp` | Browser automation |

Use the `mcp-setup` skill to configure these.

## Differences from OMC

| Feature | OMC (Claude Code) | OMK (Kimi CLI) |
|---------|-------------------|----------------|
| Agent system | Claude Agent SDK `Task()` | Kimi CLI `Agent()` |
| Model routing | haiku/sonnet/opus | Prompt-based guidance |
| Hooks | Shell hooks on lifecycle events | Skill triggers + AGENTS.md |
| Team workers | tmux + Claude CLI processes | Native Agent parallel calls |
| MCP servers | In-process MCP | `mcp-setup` skill + external CLI wrappers |
| HUD | Stdin statusline | Not supported |
| Notifications | Hook-driven | Shell curl scripts + env vars |

## Compatibility Matrix

| Launch mode | Supported | Notes |
|-------------|-----------|-------|
| Plain `kimi` | No | Does not load the OMK custom root agent |
| `kimi --agent-file <installed-agent.yaml>` | Yes | Supported bootstrap path for Kimi CLI `1.36.0` |
| Built-in Kimi subagents only | Partial | Useful for vanilla Kimi, but not the OMK workflow surface |
| OMK extended public roster | Yes | Supported when launched through the OMK `--agent-file` path |

## Verification

For Kimi CLI `1.36.0`, the minimum compatibility proof is:

1. Install OMK.
2. Launch Kimi with `--agent-file`.
3. Prove the custom root agent is active with a custom-only subagent smoke prompt such as `verifier`.
4. Run the contract check script to confirm docs, installer messaging, root registry, and skill references are aligned.

## Contributing

1. Skills live in `skills/<name>/SKILL.md`
2. Agents live in `agents/default/<name>.yaml`
3. Scripts live in `scripts/`
4. Python utilities live in `omk/`
5. Follow the [skill creator guide](https://moonshotai.github.io/kimi-cli/zh/customization/skills.html) for SKILL.md format

## License

MIT
