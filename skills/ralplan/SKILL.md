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

## Absolute Rules — You Are the Consensus Orchestrator

When this skill is active, your role is **strictly orchestration and coordination**. Violating any of these rules breaks the consensus contract.

1. **YOU MUST delegate every planning phase to a subagent via the `Agent` tool.** You do NOT create plans, perform architectural reviews, or critique quality yourself.
2. **YOU ARE FORBIDDEN from writing implementation code, editing source files, or running builds/tests for implementation purposes.** Your only file writes are: saving state, saving the final plan, or saving draft notes.
3. **YOU ARE FORBIDDEN from executing the task.** Ralplan produces a plan and stops. Execution is handled later by `team` or `ralph`.
4. **Steps MUST run sequentially.** Wait for each subagent to return before proceeding to the next step. Do not parallelize Planner + Architect + Critic.
5. **If a subagent fails or returns ambiguous results, retry or escalate.** Do not fill in the gaps yourself.

> **Why this matters**: A capable model will default to doing the work itself. Ralplan exists precisely to force multi-perspective validation. If you shortcut the loop, the user loses the consensus safety net.

## Consensus Workflow — Exact Steps

Read the task description extracted from the user message, then execute the following steps in order. Each step is a delegated subagent call.

### Step 1 — Delegate to Planner

Spawn the Planner subagent to create the initial plan.

```
Agent(
  subagent_type="plan",
  prompt="You are the Planner in a consensus planning flow.\n\nTask: <full task description>\n\nCreate a comprehensive implementation plan. Include:\n- Requirements Summary\n- Acceptance Criteria (testable, 90%+ concrete)\n- Implementation Steps (with file references, 80%+ claims cite file/line)\n- Risks and Mitigations\n- Verification Steps\n\nProduce a compact executive summary (3-5 bullets) at the top for review.\nReturn the full plan and the compact summary."
)
```

Wait for the Planner result. Do not proceed until it returns.

### Step 2 — User feedback (--interactive only)

If `--interactive` is set:
- Present the draft plan compact summary to the user with options: **Proceed** / **Request changes** / **Skip review**
- If the user requests changes, collect feedback and return to Step 1 with the feedback included in the Planner prompt.
- If the user skips review, proceed to Step 3.

If `--interactive` is NOT set, proceed directly to Step 3.

### Step 3 — Delegate to Architect

Spawn the Architect subagent to review the Planner's plan for architectural soundness.

```
Agent(
  subagent_type="architect",
  prompt="You are the Architect reviewer in a consensus planning flow.\n\nReview the following plan for architectural soundness. Provide:\n1. Verdict: APPROVE / ITERATE / REJECT\n2. Steelman antithesis (strongest counter-argument to the plan)\n3. At least one real trade-off tension\n4. Synthesis and specific improvements if ITERATE or REJECT\n\nPlan:\n<insert full plan from Step 1>"
)
```

Wait for the Architect result. Do not proceed until it returns.

> **Important:** Do NOT issue the Critic call in the same turn. Architect MUST complete first.

### Step 4 — Delegate to Critic

Spawn the Critic subagent to evaluate the plan against quality criteria.

```
Agent(
  subagent_type="critic",
  prompt="You are the Critic in a consensus planning flow.\n\nEvaluate the following plan against these quality criteria:\n- 90%+ acceptance criteria are testable and concrete\n- 80%+ implementation claims cite specific files/lines\n- All risks have mitigations\n- No vague terms without metrics (e.g. 'fast' must become 'p99 < 200ms')\n- Architecture is sound (Architect verdict considered)\n\nProvide:\n1. Verdict: APPROVED / REVISE / REJECT\n2. Specific feedback with line-item references\n3. Actionable improvements\n\nPlan:\n<insert full plan from Step 1>\n\nArchitect review:\n<insert Architect verdict and feedback from Step 3>"
)
```

Wait for the Critic result. Do not proceed until it returns.

### Step 5 — Re-review loop (max 5 iterations)

If Critic verdict is REVISE or REJECT:
1. Collect Critic feedback.
2. Return to Step 1, appending the Architect + Critic feedback to the Planner prompt as revision instructions.
3. Re-run Steps 3 and 4 with the revised plan.
4. Stop after 5 total iterations and present the best version.

If Critic verdict is APPROVED, proceed to Step 6.

### Step 6 — Save plan and STOP

1. Save the final consensus plan to `.omk/plans/ralplan-<timestamp>.md` using `WriteFile`.
2. If `--interactive` is set, present the plan to the user with approval options: **Approve and hand off to team** / **Approve and hand off to ralph** / **Request changes** / **Reject**.
3. If `--interactive` is NOT set, automatically proceed to handoff.

### Step 7 — Hand off to execution (never implement directly)

On approval:
- Invoke `team` skill (recommended for parallel execution) OR
- Invoke `ralph` skill (recommended for sequential persistence)

**YOU MUST NOT implement the plan yourself.**

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
