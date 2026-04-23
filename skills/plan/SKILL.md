---
name: plan
description: Strategic planning with optional interview workflow
triggers:
  - "plan this"
  - "plan the"
  - "let's plan"
  - "plan"
  - "review this plan"
---

# Plan

Plan creates comprehensive, actionable work plans through intelligent interaction. It auto-detects whether to interview the user (broad requests) or plan directly (detailed requests), and supports consensus mode (iterative Planner/Architect/Critic loop) and review mode (Critic evaluation of existing plans).

## Use When

- User wants to plan before implementing
- User wants structured requirements gathering for a vague idea
- User wants an existing plan reviewed
- User wants multi-perspective consensus on a plan
- Task is broad or vague and needs scoping before any code is written

## Do Not Use When

- User wants autonomous end-to-end execution — use `autopilot` instead
- User wants to start coding immediately with a clear task — use `ralph` or delegate to executor
- User asks a simple question that can be answered directly — just answer it
- Task is a single focused fix with obvious scope — skip planning, just do it

## Execution Policy

- Auto-detect interview vs direct mode based on request specificity
- Ask one question at a time during interviews — never batch multiple questions
- Gather codebase facts via `explore` agent before asking the user about them
- Plans must meet quality standards: 80%+ claims cite file/line, 90%+ criteria are testable
- Consensus mode runs fully automated by default; add `--interactive` to enable user prompts
- Consensus mode uses short deliberation by default; switch to deliberate mode with `--deliberate` or when the request explicitly signals high risk

## Mode Selection

| Mode | Trigger | Behavior |
|------|---------|----------|
| Interview | Default for broad requests | Interactive requirements gathering |
| Direct | `--direct`, or detailed request | Skip interview, generate plan directly |
| Consensus | `--consensus`, "ralplan" | Planner → Architect → Critic loop until agreement |
| Review | `--review`, "review this plan" | Critic evaluation of existing plan |

## Steps

### Interview Mode (broad/vague requests)

1. **Classify the request**: Broad (vague verbs, no specific files, touches 3+ areas) triggers interview mode
2. **Ask one focused question** using `AskUserQuestion` for preferences, scope, and constraints
3. **Gather codebase facts first**: Before asking "what patterns does your code use?", spawn an `explore` agent to find out, then ask informed follow-up questions
4. **Build on answers**: Each question builds on the previous answer
5. **Consult Analyst** for hidden requirements, edge cases, and risks
6. **Create plan** when the user signals readiness: "create the plan", "I'm ready", "make it a work plan"

### Direct Mode (detailed requests)

1. **Quick Analysis**: Optional brief Analyst consultation
2. **Create plan**: Generate comprehensive work plan immediately
3. **Review** (optional): Critic review if requested

### Consensus Mode (`--consensus` / "ralplan")

> **ORCHESTRATOR MODE — ABSOLUTE CONSTRAINTS**
> 
> In consensus mode, the root agent is **read-only and orchestration-only**. You do NOT generate the plan yourself, you do NOT perform architectural review yourself, and you do NOT critique the plan yourself. Every phase MUST be delegated to the designated subagent via the `Agent` tool. You are the coordinator; the subagents are the workers.
>
> **FORBIDDEN for root agent in consensus mode:**
> - Writing or editing implementation code
> - Running builds, tests, or lint for implementation verification
> - Creating the plan content directly (must use Planner subagent)
> - Performing architecture review directly (must use Architect subagent)
> - Performing quality critique directly (must use Critic subagent)
>
> **REQUIRED for root agent in consensus mode:**
> - Delegate each phase via the Agent tool, setting subagent_type to the appropriate role
> - Wait for each subagent result before proceeding
> - Synthesize subagent outputs
> - Save the final plan to `.omk/plans/`
> - Hand off execution to `ralph` or `team` — never implement directly

**Exact workflow:**

1. **Delegate to Planner** — Create initial plan and compact summary
   ```
   Agent(subagent_type="plan", prompt="You are the Planner in a consensus planning flow.\n\nTask: <task>\n\nCreate a comprehensive implementation plan with: Requirements Summary, Acceptance Criteria (testable), Implementation Steps (with file references), Risks and Mitigations, Verification Steps.\n\nInclude a compact executive summary (3-5 bullets) at the top.")
   ```
   Wait for Planner result before proceeding.

2. **User feedback** *(--interactive only)*: Present draft plan with options (Proceed / Request changes / Skip review)

3. **Delegate to Architect** — Review for architectural soundness
   ```
   Agent(subagent_type="architect", prompt="You are the Architect reviewer.\n\nReview this plan for architectural soundness. Provide verdict APPROVE/ITERATE/REJECT, strongest steelman antithesis, at least one real trade-off tension, and synthesis.\n\nPlan:\n<plan from Step 1>")
   ```
   Wait for Architect result before proceeding.

4. **Delegate to Critic** — Evaluate against quality criteria
   ```
   Agent(subagent_type="critic", prompt="You are the Critic.\n\nEvaluate this plan against quality criteria: 90%+ testable acceptance criteria, 80%+ claims cite files/lines, all risks have mitigations, no vague terms without metrics.\n\nProvide verdict APPROVED/REVISE/REJECT and specific feedback.\n\nPlan:\n<plan from Step 1>\n\nArchitect review:\n<architect feedback from Step 3>")
   ```
   Wait for Critic result before proceeding.

5. **Re-review loop** (max 5 iterations): If Critic rejects, collect feedback, revise with Planner (return to Step 1 with feedback), then Architect, then Critic.

6. **Apply improvements**: Merge all accepted improvements into the plan.

7. On Critic approval *(--interactive only)*: Present plan with approval options (Approve and implement / Request changes / Reject).

8. On approval: invoke `ralph` skill or `team` skill for execution — **never implement directly in the planning agent**.

> **CRITICAL — Consensus mode agent calls MUST be sequential, never parallel.** Always await the Architect result before issuing the Critic Task.

### Review Mode (`--review`)

1. Read plan file from `.omk/plans/`
2. Evaluate via Critic using `Agent(subagent_type="critic", ...)`
3. Return verdict: APPROVED, REVISE (with specific feedback), or REJECT

## Plan Output Format

Every plan includes:
- Requirements Summary
- Acceptance Criteria (testable)
- Implementation Steps (with file references)
- Risks and Mitigations
- Verification Steps

Plans are saved to `.omk/plans/`. Drafts go to `.omk/drafts/`.

## Tool Usage

- Use `AskUserQuestion` for preference questions (scope, priority, timeline, risk tolerance)
- Use `explore` agent to gather codebase facts before asking the user
- Use `Agent(subagent_type="plan", ...)` for planning validation on large-scope plans
- Use `Agent(subagent_type="analyst", ...)` for requirements analysis
- Use `Agent(subagent_type="critic", ...)` for plan review in consensus and review modes
- **CRITICAL — Consensus mode agent calls MUST be sequential, never parallel.** Always await the Architect result before issuing the Critic Task.

## Examples

**Good** — Adaptive interview:
```
[spawns explore agent: "find authentication implementation"]
[receives: "Auth is in src/auth/ using JWT with passport.js"]
"I see you're using JWT authentication with passport.js in src/auth/.
 For this new feature, should we extend the existing auth or add a separate auth flow?"
```

**Bad** — Batching multiple questions:
```
"What's the scope? And the timeline? And who's the audience?"
```

## Escalation and Stop Conditions

- Stop interviewing when requirements are clear enough to plan
- In consensus mode, stop after 5 iterations and present the best version
- If the user says "just do it" or "skip planning", transition to `ralph` skill for execution
- Escalate to the user when there are irreconcilable trade-offs

## Final Checklist

- [ ] Plan has testable acceptance criteria (90%+ concrete)
- [ ] Plan references specific files/lines where applicable (80%+ claims)
- [ ] All risks have mitigations identified
- [ ] No vague terms without metrics ("fast" -> "p99 < 200ms")
- [ ] Plan saved to `.omk/plans/`
