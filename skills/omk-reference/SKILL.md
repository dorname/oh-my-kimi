---
name: omk-reference
description: OMK agent catalog, available tools, team pipeline routing, commit protocol,
  and skills registry
metadata:
  triggers: []
  user-invocable: false
---

# OMK Reference

Auto-loaded reference for OMK agent catalog, tools, pipeline routing, and skills registry.

## Agent Catalog

### Build/Analysis Lane

| Agent | Description | When to Use |
|-------|-------------|-------------|
| `coder` | General software engineering | General implementation tasks |
| `explore` | Fast codebase search | Quick lookups, finding files |
| `analyst` | Requirements clarity | Broad requests, vague requirements |
| `plan` | Task sequencing | Before multi-file implementations |
| `architect` | System design | Complex refactors, new features |
| `debugger` | Root-cause analysis | Build errors, test failures |
| `executor` | Implementation | The default for coding tasks |
| `verifier` | Completion evidence | Before claiming done |
| `tracer` | Causal tracing | Complex bugs, incidents |

### Review Lane

| Agent | Description | When to Use |
|-------|-------------|-------------|
| `code-reviewer` | Comprehensive review | Pre-merge quality gate |
| `security-reviewer` | Security audit | Security-critical changes |

### Domain Specialists

| Agent | Description | When to Use |
|-------|-------------|-------------|
| `test-engineer` | Test strategy | Adding or improving tests |
| `designer` | UI/UX design | Frontend work |
| `writer` | Documentation | Docs, guides |
| `document-specialist` | External docs | Unknown SDKs |
| `code-simplifier` | Code clarity | Cleanup passes |
| `scientist` | Data analysis | Data-heavy tasks |

### Coordination

| Agent | Description | When to Use |
|-------|-------------|-------------|
| `critic` | Plan review | Before committing to plans |

## Tools

### Kimi CLI Native Tools

- `ReadFile`, `WriteFile`, `StrReplaceFile` — File operations
- `Glob`, `Grep` — Search
- `Shell` — Command execution
- `SearchWeb`, `FetchURL` — Web access
- `AskUserQuestion` — User interaction
- `SetTodoList` — Task tracking
- `Agent` — Subagent delegation
- `TaskList`, `TaskOutput`, `TaskStop` — Background task management
- `ExitPlanMode`, `EnterPlanMode` — Planning mode

### OMK Scripts

- `scripts/lsp-diagnostics.sh` — IDE-like diagnostics
- `scripts/ast-search.sh` — Structural code search
- `scripts/notify.sh` — Notifications

## Skills Registry

| Skill | Trigger | Description |
|-------|---------|-------------|
| `autopilot` | "autopilot", "build me" | Full autonomous execution |
| `ralph` | "ralph", "don't stop" | Persistence loop |
| `ultrawork` | "ultrawork", "parallel" | Parallel execution |
| `team` | "team" | Coordinated agents |
| `plan` | "plan this" | Strategic planning |
| `deep-interview` | "deep interview" | Requirements gathering |
| `ultraqa` | "ultraqa" | QA cycling |
| `cancel` | "cancel", "stop" | Cancel modes |

## Team Pipeline

`team-plan -> team-exec -> team-verify -> team-fix (loop)`

## Commit Protocol

1. Ask for confirmation before destructive git operations
2. Write clear, atomic commits
3. Prefer rebase for clean history
4. Never force-push to shared branches
