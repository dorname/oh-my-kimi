---
name: team
description: N coordinated agents on shared task list
triggers:
  - "team"
---

# Team

Spawn N coordinated agents working on a shared task list. In OMK, team mode uses Kimi CLI's native `Agent` tool for parallel delegation rather than tmux processes.

## Usage

```
team 3:executor "fix all TypeScript errors across the project"
team "refactor the auth module with security review"
team ralph "build a complete REST API for user management"
```

## Parameters

- **N** - Number of agents (1-6). Optional; defaults to auto-sizing based on task decomposition.
- **agent-type** - Agent to spawn for execution (e.g., executor, debugger, designer). Optional; defaults to stage-aware routing.
- **task** - High-level task to decompose and distribute
- **ralph** - Optional modifier. When present, wraps the team pipeline in Ralph's persistence loop.

## Architecture

```
User: "team 3:executor fix all TypeScript errors"
        |
        v
[Leader (current session)]
        |
        +-- Analyze & decompose task into subtasks
        |       -> explore/architect produces subtask list
        |
        +-- Agent(subagent_type="executor", prompt="subtask 1") [parallel]
        +-- Agent(subagent_type="executor", prompt="subtask 2") [parallel]
        +-- Agent(subagent_type="executor", prompt="subtask 3") [parallel]
        |
        +-- Collect results, verify, report
```

## Staged Pipeline

Team execution follows a staged pipeline:

`team-plan -> team-exec -> team-verify -> team-fix (loop)`

### Stage Agent Routing

| Stage | Primary Agents | When to Use |
|-------|---------------|-------------|
| **team-plan** | `explore`, `planner` | Decompose task, create task graph |
| **team-exec** | `executor`, `debugger`, `designer` | Execute subtasks in parallel |
| **team-verify** | `verifier`, `code-reviewer`, `security-reviewer` | Validate results |
| **team-fix** | `executor`, `debugger` | Fix defects from verification |

### Stage Entry/Exit Criteria

- **team-plan**: Entry on invocation. Exit when decomposition is complete.
- **team-exec**: Entry after planning. Exit when all subtasks complete.
- **team-verify**: Entry after execution. Exit on pass (no fixes needed) or fail (move to team-fix).
- **team-fix**: Entry on verification failure. Exit when fixes complete, then loop to team-exec.

## Workflow

### Phase 1: Parse Input

- Extract **N** (agent count), validate 1-6
- Extract **agent-type**, validate it maps to a known agent
- Extract **task** description

### Phase 2: Analyze & Decompose

Use `explore` or `architect` agent to analyze the codebase and break the task into subtasks:

- Each subtask should be file-scoped or module-scoped to avoid conflicts
- Subtasks must be independent or have clear dependency ordering
- Each subtask needs a concise subject and detailed description

Write task list to `.omk/state/team-tasks.json`.

### Phase 3: Execute in Parallel

Launch all parallel-safe subtasks simultaneously using `Agent` tool:

```
Agent(subagent_type="executor", prompt="Fix type errors in src/auth/login.ts: ...")
Agent(subagent_type="executor", prompt="Fix type errors in src/api/users.ts: ...")
Agent(subagent_type="executor", prompt="Fix type errors in src/utils/helpers.ts: ...")
```

**Key rules:**
- Spawn all agents in parallel (they run concurrently)
- Do NOT wait for one to finish before spawning the next
- Each agent works independently on its assigned subtask

### Phase 4: Monitor & Coordinate

- Track completion status of each agent
- If an agent reports failure, decide: retry, reassign, or skip
- Handle dependency blockers (wait for prerequisite subtasks before launching dependents)

### Phase 5: Verify

When all agents complete:

1. Run build/test/lint to verify no regressions
2. Delegate to `verifier` agent for completion check
3. For security/auth changes: add `security-reviewer`
4. For large changes (>20 files): add `code-reviewer`

### Phase 6: Completion

When verification passes:

1. Report summary to user
2. Clean up `.omk/state/team-state.json`
3. If linked to ralph, continue with ralph verification loop

## State Management

Team state is stored in `.omk/state/team-state.json`:

```json
{
  "active": true,
  "current_phase": "team-plan|team-exec|team-verify|team-fix",
  "agent_count": 3,
  "agent_type": "executor",
  "task": "fix all TypeScript errors",
  "fix_loop_count": 0,
  "max_fix_loops": 3,
  "linked_ralph": false
}
```

## Error Handling

### Agent Fails a Task

1. Read the agent's error output
2. Decide: retry (same task), reassign (different agent), or skip
3. If retrying, include the error context in the new prompt

### Dependency Blocked

1. If a blocking task fails, decide whether to:
   - Retry the blocker
   - Remove the dependency and proceed independently
   - Skip the blocked task entirely

## Team + Ralph Composition

When the user invokes `team ralph`, team mode wraps itself in Ralph's persistence loop:

1. Ralph outer loop starts (iteration 1)
2. Team pipeline runs: `team-plan -> team-exec -> team-verify`
3. If `team-verify` passes: Ralph runs architect verification
4. If architect approves: both modes complete
5. If `team-verify` fails OR architect rejects: team enters `team-fix`, then loops back
6. If fix loop exceeds `max_fix_loops`: Ralph increments iteration and retries

## Configuration

Optional settings in `.omk/config.json`:

```json
{
  "team": {
    "maxAgents": 6,
    "maxFixLoops": 3
  }
}
```

## Cancellation

The `cancel` skill handles team cleanup:

1. Read team state from `.omk/state/team-state.json`
2. Mark all active subtasks as cancelled
3. Clear state file
4. If linked to ralph, also clear ralph state

## Comparison: OMK Team vs OMC Team

| Aspect | OMC Team | OMK Team |
|--------|----------|-----------|
| Workers | tmux + Claude CLI processes | Native Agent parallel calls |
| Communication | SendMessage/TaskList | Direct result collection |
| Dependencies | TaskUpdate blockedBy | Explicit dependency ordering in prompt |
| State | `~/.claude/teams/` | `.omk/state/team-state.json` |
| Shutdown | Graceful request/response | Result collection + state cleanup |

**Advantage**: OMK Team is lighter, requires no tmux, and works cross-platform.
