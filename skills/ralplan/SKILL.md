---
name: ralplan
description: Consensus planning entrypoint that auto-gates vague ralph/autopilot/team
  requests before execution
metadata:
  triggers:
  - ralplan
  - consensus plan
---

# Ralplan

> **CRITICAL — EXECUTE IMMEDIATELY**: This file was loaded via `/skill:ralplan` or `/flow:ralplan`. You MUST execute the consensus workflow below RIGHT NOW. Do NOT summarize, analyze, or check trigger words. The user's task description follows the `User request:` line.

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
  description="Create consensus plan",
  prompt="You are the Planner in a consensus planning flow.\n\nTask: <full task description>\n\nRevision instructions (if any): <revision_instructions>\n\nCreate a comprehensive implementation plan. Include:\n- Requirements Summary\n- Acceptance Criteria (testable, 90%+ concrete)\n- Implementation Steps (with file references, 80%+ claims cite file/line)\n- Risks and Mitigations\n- Verification Steps\n\nRevision history:\n<revision_history>\n\nProduce a compact executive summary (3-5 bullets) at the top for review.\nReturn the full plan and the compact summary."
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
  subagent_type="coder",
  description="Review architecture soundness",
  prompt="You are the Architect reviewer in a consensus planning flow.\n\nReview the following plan for architectural soundness. Provide:\n1. Verdict: APPROVE / ITERATE / REJECT\n2. Steelman antithesis (strongest counter-argument to the plan)\n3. At least one real trade-off tension\n4. Synthesis and specific improvements if ITERATE or REJECT\n\nPlan:\n<insert full plan from Step 1>"
)
```

Wait for the Architect result. Do not proceed until it returns.

> **Important:** Do NOT issue the Critic call in the same turn. Architect MUST complete first.

### Step 3.5 — Architect Pre-Review Gate

- Spawn an `architect` subagent with the current plan draft and request a verdict of APPROVE, ITERATE, or REJECT before applying the routing rules below.
- **APPROVE**: Proceed to Step 4.
- **ITERATE**: Route to Step 5a.
- **REJECT**: Route to Step 5b (early termination). Record the Architect rejection rationale for the termination summary.

### Step 4 — Delegate to Critic

Spawn the Critic subagent to evaluate the plan against quality criteria.

```
Agent(
  subagent_type="coder",
  description="Critique plan quality",
  prompt="You are the Critic in a consensus planning flow.\n\nEvaluate the following plan against these quality criteria:\n- 90%+ acceptance criteria are testable and concrete\n- 80%+ implementation claims cite specific files/lines\n- All risks have mitigations\n- No vague terms without metrics (e.g. 'fast' must become 'p99 < 200ms')\n- Architecture is sound (Architect verdict considered)\n\nProvide:\n1. Verdict: APPROVED / REVISE / REJECT\n2. Specific feedback with line-item references\n3. Actionable improvements\n\nPlan:\n<insert full plan from Step 1>\n\nArchitect review:\n<insert Architect verdict and feedback from Step 3>"
)
```

Wait for the Critic result. Do not proceed until it returns.

### Step 5 — Consensus Loop (maximum of 5 revision cycles)

**Iteration counter:** Initialize to 1 before the first Planner call. Increment by 1 each time the Planner is re-invoked with revision instructions. After each increment, write the current counter value to `.omk/drafts/ralplan-cycle-counter.txt` and read it at the start of each round to enforce the max-cycle check. The default maximum is 5; this threshold is configurable (e.g., `RALPLAN_MAX_CYCLES`).

#### 5a. Revision path

If the Critic verdict is REVISE or REJECT, or if the Architect Pre-Review Gate routed an ITERATE verdict here:

1. Collect the relevant feedback (Critic and/or Architect).
2. **Replace** (do not append) the `<revision_instructions>` placeholder in the Step 1 Planner prompt with the new revision instructions.
3. Preserve prior revision history by appending the superseded instructions to the `<revision_history>` placeholder.
4. After placeholder substitution, return to Step 2 and re-run Steps 3, 3.5, and 4.
5. If the iteration counter equals 5, route to Step 5b instead of returning to Step 1.
6. **Feedback compaction guard**: If the current cycle's feedback payload intended for the `<revision_instructions>` placeholder exceeds 2000 tokens, spawn a `coder` subagent with prompt "Summarize the following feedback into under 2000 tokens while preserving all actionable items and line references:" and use the summary as the new revision instructions.
7. **Compaction failure fallback**: If the compaction subagent invocation times out or errors, fall back to uncompressed feedback and emit a warning.

#### 5b. Termination

If the consensus loop reaches the maximum of 5 revision cycles without Critic approval, or if the Architect Pre-Review Gate routes a REJECT verdict here, stop iterating and present the best available plan version. On REJECT, include the Architect rejection rationale in the termination summary. Stop the workflow here. Do not proceed to Step 6 or execution handoff.

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
