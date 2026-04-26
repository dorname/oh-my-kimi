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
| `coder` | General software engineering tasks; general implementation tasks | General implementation tasks |
| `explore` | Fast codebase exploration with prompt-enforced read-only behavior; quick lookups, finding files | Quick lookups, finding files |
| `analyst` | Requirements clarity, acceptance criteria, and hidden constraints; broad requests, vague requirements | Broad requests, vague requirements |
| `plan` | Read-only implementation planning and architecture design; before multi-file implementations | Before multi-file implementations |
| `architect` | System design, boundaries, interfaces, and long-horizon tradeoffs; complex refactors, new features | Complex refactors, new features |
| `debugger` | Root-cause analysis, regression isolation, and failure diagnosis; build errors, test failures, bugs | Build errors, test failures |
| `executor` | Code implementation, refactoring, and feature work; the default for coding tasks | The default for coding tasks |
| `verifier` | Completion evidence, claim validation, and test adequacy; before claiming done | Before claiming done |
| `tracer` | Evidence-driven causal tracing and competing hypotheses; complex bugs, incidents | Complex bugs, incidents |

### Review Lane

| Agent | Description | When to Use |
|-------|-------------|-------------|
| `code-reviewer` | Comprehensive code review across logic, maintainability, and quality; pre-merge quality gate | Pre-merge quality gate |
| `security-reviewer` | Security vulnerabilities, trust boundaries, and authn/authz review; security-critical changes | Security-critical changes |

### Domain Specialists

| Agent | Description | When to Use |
|-------|-------------|-------------|
| `test-engineer` | Test strategy, coverage improvements, and flaky-test hardening; adding or improving tests | Adding or improving tests |
| `designer` | UI/UX architecture and interaction design; frontend work | Frontend work |
| `writer` | Documentation, migration notes, and user guidance; docs, guides | Docs, guides |
| `document-specialist` | Official documentation lookup and external API reference guidance; unknown SDKs | Unknown SDKs |
| `code-simplifier` | Code clarity, simplification, and cleanup passes; cleanup passes | Cleanup passes |
| `scientist` | Parallel scientific and data-heavy analysis; data-heavy tasks | Data-heavy tasks |

### Coordination

| Agent | Description | When to Use |
|-------|-------------|-------------|
| `critic` | Plan and design critical challenge; before committing to plans | Before committing to plans |

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
| `plan` | Read-only implementation planning and architecture design; before multi-file implementations | Strategic planning |
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