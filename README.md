# OMK (Kimi Orchestration & Multi-agent Coordination)

> Oh-My-Kimi. Multi-agent orchestration for [Kimi Code CLI](https://github.com/MoonshotAI/kimi-cli). 36 skills, 18 public specialist agents, and stateful execution.

## Overview

OMK ports the full OMC multi-agent orchestration experience to Kimi CLI. It provides:

- **36 skills** — autopilot, ralph, ultrawork, team, plan, deep-dive, and more
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
# 注意：以下路径在执行 ./install.sh 后才会生成
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

## Uninstall

```bash
# Remove OMK skills, agent configs, and the omk Python package
./uninstall.sh

# Project-local uninstall
./uninstall.sh --project

# Uninstall from a specific project
./uninstall.sh --target-dir ~/my-project

# Preview what would be removed (no changes)
./uninstall.sh --dry-run

# Skip confirmation prompt
./uninstall.sh --force

# Keep the .omk/ runtime state directory
./uninstall.sh --keep-state
```

### Uninstall Options

| Option | Description |
|--------|-------------|
| `--project` | Uninstall from `./.kimi/skills/` (project-local) |
| `--target-dir DIR` | Uninstall from `DIR/.kimi/skills/` |
| `--keep-state` | Preserve the `.omk/` runtime state directory |
| `--force` | Skip confirmation prompt |
| `--dry-run` | Preview what would be removed |
| `--help` | Show full help |

## Architecture

```
User Input → kimi --agent-file .kimi/agents/agent.yaml → Skill Detection → Agent Orchestration → Tools & State
                                                           │                    │
                                                           ▼                    ▼
                                                    .kimi/skills/         Agent YAML configs
                                                    (36 SKILL.md)        (18 public roles)
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
| `ralph` | "ralph", "don't stop", "must complete" | Self-referential loop until task completion with configurable verification reviewer |
| `ultrawork` | "ultrawork", "ulw", "parallel" | Parallel execution engine for high-throughput task completion |
| `team` | "team" | N coordinated agents on shared task list |
| `plan` | Read-only implementation planning and architecture design; task sequencing, execution plans, and risk flags | Strategic planning with optional interview |
| `ralplan` | "ralplan", "consensus plan" | Consensus planning entrypoint that auto-gates vague ralph/autopilot/team requests before execution |
| `deep-interview` | "deep interview", "interview me" | Socratic deep interview with ambiguity gating |
| `deep-dive` | "deep dive" | 2-stage pipeline: trace → deep-interview |
| `ultraqa` | "ultraqa" | QA cycling — test, verify, fix, repeat |
| `ai-slop-cleaner` | "cleanup", "deslop", "anti-slop" | Clean AI-generated code slop with a regression-safe, deletion-first workflow |
| `visual-verdict` | "visual verdict" | Structured visual QA for screenshot comparisons |
| `trace` | "trace" | Evidence-driven tracing with competing hypotheses |
| `ccg` | "ccg" | Claude-Codex-Gemini tri-model orchestration |
| `sciomk` | "sciomk" | Parallel scientist agents for comprehensive analysis |
| `self-improve` | "self-improve" | Autonomous evolutionary code improvement |

### Utilities

| Skill | Trigger | Description |
|-------|---------|-------------|
| `cancel` | "cancel", "stop", "abort" | Cancel any active OMK mode |
| `ask` | "ask" | Process-first advisor routing for Claude, Codex, or Gemini via natural language |
| `setup` | "setup" | Install or refresh OMK components |
| `omk-doctor` | "doctor" | Diagnose and fix OMK installation issues |
| `verify` | "verify" | Verify that a change really works |
| `debug` | "debug" | Diagnose current session or repo state |
| `release` | "release" | Generic release assistant |
| `skill` | "skill" | Manage local skills |
| `skillify` | "skillify" | Turn a repeatable workflow from the current session into a reusable OMK skill draft |
| `configure-notifications` | "configure notifications" | Configure Telegram, Discord, Slack |
| `mcp-setup` | "mcp setup" | Configure external tools and integrations for enhanced agent capabilities |
| `deepinit` | "deepinit", "deep init" | Deep codebase initialization with hierarchical AGENTS.md documentation |
| `external-context` | "external context", "look up docs", "search docs" | Invoke parallel document-specialist agents for external web searches and documentation lookup |
| `project-session-manager` | "project session", "psm", "worktree" | Worktree-first dev environment manager for issues, PRs, and features |

### Memory & Knowledge

| Skill | Trigger | Description |
|-------|---------|-------------|
| `learner` | "learner" | Extract a learned skill from conversation |
| `wiki` | "wiki" | Persistent markdown knowledge base |
| `writer-memory` | "writer-memory" | Agentic memory system for writers — track characters, relationships, scenes, and themes |
| `remember` | "remember" | Review reusable project knowledge |
| `omk-reference` | (auto-load) | OMK agent catalog, available tools, team pipeline routing, commit protocol, and skills registry |

### Deprecated

| Skill | Trigger | Description |
|-------|---------|-------------|
| `hud` | "hud", "status bar" | Configure HUD display options (deprecated in OMK — Kimi CLI does not support stdin status bars) |
| `omk-teams` | "omk-teams" | Deprecated in OMK — use `team` skill instead. Original OMC skill for tmux CLI workers. |

See `skills/` for the complete catalog.

## Agent Catalog

Invoke via `Agent(subagent_type="<name>", ...)`.

### Build/Analysis Lane

| Agent | Description | When to Use |
|-------|-------------|-------------|
| `coder` | General software engineering tasks | Small or mixed implementation work |
| `explore` | Fast codebase exploration with prompt-enforced read-only behavior; quick search and file/symbol mapping | Quick lookups, finding files, understanding structure |
| `analyst` | Requirements clarity, acceptance criteria, hidden constraints | Broad requests, vague requirements |
| `plan` | Read-only implementation planning and architecture design; task sequencing, execution plans, and risk flags | Before multi-file implementations |
| `architect` | System design, boundaries, interfaces, long-horizon tradeoffs | Complex refactors, new features |
| `debugger` | Root-cause analysis, regression isolation, failure diagnosis | Build errors, test failures, bugs |
| `executor` | Code implementation, refactoring, feature work | The default for coding tasks |
| `verifier` | Completion evidence, claim validation, test adequacy | Before claiming done |
| `tracer` | Evidence-driven causal tracing and competing hypotheses; complex bugs and incidents | Causal investigation |

### Review Lane

| Agent | Description | When to Use |
|-------|-------------|-------------|
| `code-reviewer` | Comprehensive code review across logic, maintainability, and quality; pre-merge quality gate | Pre-merge quality gate |
| `security-reviewer` | Security vulnerabilities, trust boundaries, and authn/authz review; security-critical changes | Security-critical changes |

### Domain Specialists

| Agent | Description | When to Use |
|-------|-------------|-------------|
| `test-engineer` | Test strategy, coverage improvements, and flaky-test hardening; adding or improving tests | Adding or improving tests |
| `designer` | UI/UX architecture and interaction design; frontend work, styling | Frontend work, styling |
| `writer` | Documentation, migration notes, and user guidance; docs, guides | Documentation tasks |
| `document-specialist` | Official documentation lookup and external API reference guidance; unknown SDKs, frameworks | Unknown SDKs, frameworks |
| `code-simplifier` | Code clarity, simplification, maintainability | Cleanup, deslop passes |
| `scientist` | Parallel scientific and data-heavy analysis; data-heavy tasks | Data-heavy tasks |

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

1. **Install OMK** (`./install.sh` or `./install.sh --project`).
2. **Run contract checks**:
   ```bash
   python3 scripts/check-agent-contract.py   # registry, docs, taxonomy, YAML validity
   python3 tests/test_check_agent_contract.py # unit tests for extractors
   ```
3. **Run smoke test** (no Kimi CLI required for static checks):
   ```bash
   ./scripts/smoke-test.sh          # project-local
   ./scripts/smoke-test.sh --global # global install
   ```
4. **Launch Kimi with `--agent-file`**:
   ```bash
   kimi --agent-file .kimi/agents/agent.yaml
   ```
5. **Prove the custom root agent is active** with a custom-only subagent smoke prompt such as `verifier`.
6. **Trigger a skill** (e.g. `autopilot: say hello`) to confirm skills are discovered and loaded.

## Contributing

1. Skills live in `skills/<name>/SKILL.md`
2. Agents live in `agents/default/<name>.yaml`
3. Scripts live in `scripts/`
4. Python utilities live in `omk/`
5. Follow the [skill creator guide](https://moonshotai.github.io/kimi-cli/zh/customization/skills.html) for SKILL.md format

## License

MIT