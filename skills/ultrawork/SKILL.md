---
name: ultrawork
description: Parallel execution engine for high-throughput task completion
triggers:
  - "ultrawork"
  - "ulw"
  - "parallel"
---

# Ultrawork

Ultrawork is a parallel execution engine that runs multiple agents simultaneously for independent tasks. It is a component, not a standalone persistence mode — it provides parallelism but not persistence, verification loops, or state management.

## Use When

- Multiple independent tasks can run simultaneously
- You need to delegate work to multiple agents at once
- Task benefits from concurrent execution but the user will manage completion themselves

## Do Not Use When

- Task requires guaranteed completion with verification — use `ralph` instead (ralph includes ultrawork)
- Task requires a full autonomous pipeline — use `autopilot` instead
- There is only one sequential task with no parallelism opportunity — delegate directly to an executor agent
- User needs session persistence for resume — use `ralph`

## Execution Policy

- Fire all independent agent calls simultaneously — never serialize independent work
- Use `run_in_background=true` for operations over ~30 seconds (installs, builds, tests)
- Run quick commands (git status, file reads, simple checks) in the foreground

## Steps

1. **Classify tasks by independence**: Identify which tasks can run in parallel vs which have dependencies
2. **Route to correct complexity**:
   - Simple lookups/definitions: `Agent(subagent_type="explore", prompt="...")`
   - Standard implementation: `Agent(subagent_type="executor", prompt="...")`
   - Complex analysis/refactoring: `Agent(subagent_type="architect", prompt="...")`
3. **Fire independent tasks simultaneously**: Launch all parallel-safe tasks at once
4. **Run dependent tasks sequentially**: Wait for prerequisites before launching dependent work
5. **Background long operations**: Builds, installs, and test suites use `run_in_background=true`
6. **Verify when all tasks complete** (lightweight):
   - Build/typecheck passes
   - Affected tests pass
   - No new errors introduced

## Tool Usage

- Use `Agent(subagent_type="executor", ...)` for implementation tasks
- Use `Agent(subagent_type="explore", ...)` for simple lookups and codebase search
- Use `Agent(subagent_type="architect", ...)` for complex analysis and refactoring
- Use `run_in_background=true` for package installs, builds, and test suites
- Use foreground execution for quick status checks and file operations

## Examples

**Good** — Three independent tasks fired simultaneously:
```
Agent(subagent_type="coder", prompt="Add missing type export for Config interface")
Agent(subagent_type="executor", prompt="Implement the /api/users endpoint with validation")
Agent(subagent_type="executor", prompt="Add integration tests for the auth middleware")
```

**Good** — Background execution:
```
Agent(subagent_type="executor", prompt="npm install && npm run build", run_in_background=true)
Agent(subagent_type="coder", prompt="Update the README with new API endpoints")
```

**Bad** — Sequential execution of independent work:
```
# DON'T DO THIS — these are independent and should run in parallel
result1 = Agent(coder, "Add type export")   # wait...
result2 = Agent(executor, "Implement endpoint")  # wait...
result3 = Agent(executor, "Add tests")           # wait...
```

## Escalation and Stop Conditions

- When ultrawork is invoked directly (not via ralph), apply lightweight verification only
- For full persistence and comprehensive verification, recommend switching to `ralph` mode
- If a task fails repeatedly across retries, report the issue rather than retrying indefinitely
- Escalate to the user when tasks have unclear dependencies or conflicting requirements

## Final Checklist

- [ ] All parallel tasks completed
- [ ] Build/typecheck passes
- [ ] Affected tests pass
- [ ] No new errors introduced
