---
name: ralplan
description: Consensus planning entrypoint that auto-gates vague ralph/autopilot/team requests before execution
triggers:
  - "ralplan"
  - "consensus plan"
---

# Ralplan

Ralplan is a shorthand alias for `plan --consensus`. It triggers iterative planning with Planner, Architect, and Critic agents until consensus is reached, with structured deliberation (short mode by default, deliberate mode for high-risk work).

## Usage

```
ralplan "task description"
ralplan --interactive "task description"
ralplan --deliberate "task description"
```

## Flags

- `--interactive`: Enables user prompts at key decision points (draft review and final approval). Without this flag the workflow runs fully automated.
- `--deliberate`: Forces deliberate mode for high-risk work. Adds pre-mortem (3 scenarios) and expanded test planning.
- `--architect codex`: Use Codex for the Architect pass when Codex CLI is available.
- `--critic codex`: Use Codex for the Critic pass when Codex CLI is available.

## Behavior

This skill invokes the Plan skill in consensus mode. Follow the Plan skill's full documentation for consensus mode details.

The consensus workflow:
1. **Planner** creates initial plan and a compact summary before review
2. **User feedback** *(--interactive only)*: Present draft plan with options
3. **Architect** reviews for architectural soundness — **await completion before step 4**
4. **Critic** evaluates against quality criteria — run only after step 3 completes
5. **Re-review loop** (max 5 iterations): Any rejection runs the full closed loop
6. On Critic approval *(--interactive only)*: Present plan with approval options
7. On approval: invoke `team` skill or `ralph` skill for execution — never implement directly

> **Important:** Steps 3 and 4 MUST run sequentially. Do NOT issue both agent calls in the same parallel batch.

## Pre-Execution Gate

### Why the Gate Exists

Execution modes (ralph, autopilot, team, ultrawork) spin up heavy multi-agent orchestration. When launched on a vague request like "ralph improve the app", agents have no clear target — they waste cycles on scope discovery.

The ralplan-first gate intercepts underspecified execution requests and redirects them through the ralplan consensus planning workflow. This ensures:
- **Explicit scope**: A PRD defines exactly what will be built
- **Test specification**: Acceptance criteria are testable before code is written
- **Consensus**: Planner, Architect, and Critic agree on the approach
- **No wasted execution**: Agents start with a clear, bounded task

### Good vs Bad Prompts

**Passes the gate** (specific enough for direct execution):
- `ralph fix the null check in src/hooks/bridge.ts:326`
- `autopilot implement issue #42`
- `team add validation to function processKeywordDetector`
- `ralph do: 1. Add input validation 2. Write tests 3. Update README`

**Gated — redirected to ralplan** (needs scoping first):
- `ralph fix this`
- `autopilot build the app`
- `team improve performance`
- `ralph add authentication`

**Bypass the gate** (when you know what you want):
- `force: ralph refactor the auth module`

### When the Gate Does NOT Trigger

The gate auto-passes when it detects any concrete signal:

| Signal Type | Example | Why it passes |
|---|---|---|
| File path | `ralph fix src/hooks/bridge.ts` | References a specific file |
| Issue/PR number | `ralph implement #42` | Has a concrete work item |
| camelCase symbol | `ralph fix processKeywordDetector` | Names a specific function |
| Numbered steps | `ralph do: 1. Add X 2. Test Y` | Structured deliverables |
| Code block | `ralph add: \`\`\`ts ... \`\`\`` | Concrete code provided |
| Escape prefix | `force: ralph do it` | Explicit user override |

## End-to-End Flow Example

1. User types: `ralph add user authentication`
2. Gate detects: execution keyword (`ralph`) + underspecified prompt
3. Gate redirects to **ralplan** with message explaining the redirect
4. Ralplan consensus runs: Planner → Architect → Critic
5. On consensus approval, user chooses execution path:
   - **team**: parallel coordinated agents (recommended)
   - **ralph**: sequential execution with verification
6. Execution begins with a clear, bounded plan
