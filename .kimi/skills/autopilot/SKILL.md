---
name: autopilot
description: Full autonomous execution from idea to working code
triggers:
  - "autopilot"
  - "auto pilot"
  - "autonomous"
  - "build me"
  - "create me"
  - "make me"
  - "full auto"
  - "handle it all"
  - "I want a"
  - "I want an"
---

# Autopilot

Autopilot takes a brief product idea and autonomously handles the full lifecycle: requirements analysis, technical design, planning, parallel implementation, QA cycling, and multi-perspective validation. It produces working, verified code from a 2-3 line description.

## Use When

- User wants end-to-end autonomous execution from an idea to working code
- Task requires multiple phases: planning, coding, testing, and validation
- User wants hands-off execution and is willing to let the system run to completion

## Do Not Use When

- User wants to explore options or brainstorm — use `plan` skill instead
- User wants a single focused code change — use `ralph` or delegate to an executor agent
- User wants to review or critique an existing plan — use `plan --review`
- Task is a quick fix or small bug — use direct executor delegation

## Execution Policy

- Each phase must complete before the next begins
- Parallel execution is used within phases where possible (Phase 2 and Phase 4)
- QA cycles repeat up to 5 times; if the same error persists 3 times, stop and report the fundamental issue
- Validation requires approval from all reviewers; rejected items get fixed and re-validated
- Cancel with `cancel` skill at any time; progress is preserved for resume

## State Management

Autopilot state is stored in `.omk/state/autopilot-state.json`:

```json
{
  "active": true,
  "current_phase": "expansion|planning|execution|qa|validation|cleanup",
  "phase_history": ["expansion", "planning", ...],
  "spec_path": ".omk/plans/autopilot-spec.md",
  "plan_path": ".omk/plans/autopilot-impl.md",
  "qa_cycles": 0,
  "max_qa_cycles": 5,
  "validation_rounds": 0,
  "max_validation_rounds": 3
}
```

Write state at the start of each phase using:
```
WriteFile(path=".omk/state/autopilot-state.json", content=<json>)
```

## Phases

### Phase 0 - Expansion

Turn the user's idea into a detailed spec.

- **If ralplan consensus plan exists** (`.omk/plans/ralplan-*.md` or `.omk/plans/consensus-*.md`): Skip BOTH Phase 0 and Phase 1 — jump directly to Phase 2 (Execution).
- **If deep-interview spec exists** (`.omk/specs/deep-interview-*.md`): Skip analyst+architect expansion, use the pre-validated spec directly as Phase 0 output. Continue to Phase 1.
- **If input is vague** (no file paths, function names, or concrete anchors): Offer redirect to `deep-interview` for Socratic clarification before expanding.
- **Otherwise**: Delegate to `analyst` agent for requirements extraction, then `architect` agent for technical specification.

**Output**: `.omk/plans/autopilot-spec.md`

### Phase 1 - Planning

Create an implementation plan from the spec.

- **If ralplan consensus plan exists**: Skip — already done.
- Delegate to `architect` agent to create plan (direct mode, no interview).
- Delegate to `critic` agent to validate plan.

**Output**: `.omk/plans/autopilot-impl.md`

### Phase 2 - Execution

Implement the plan using parallel agent delegation.

- Delegate to `executor` agents for implementation tasks:
  - Simple tasks: `Agent(subagent_type="coder", prompt="...")`
  - Standard tasks: `Agent(subagent_type="executor", prompt="...")`
  - Complex analysis: `Agent(subagent_type="architect", prompt="...")`
- Run independent tasks in parallel (fire all independent Agent calls simultaneously)
- Use `run_in_background=true` for long operations (installs, builds, test suites)

### Phase 3 - QA

Cycle until all tests pass.

- Build, lint, test, fix failures
- Repeat up to 5 cycles
- Stop early if the same error repeats 3 times (indicates a fundamental issue)

Use Shell to run build/test commands and read output.

### Phase 4 - Validation

Multi-perspective review in parallel.

- `Agent(subagent_type="architect", prompt="Review functional completeness of <changes>")`
- `Agent(subagent_type="security-reviewer", prompt="Check for vulnerabilities in <changes>")`
- `Agent(subagent_type="code-reviewer", prompt="Review code quality of <changes>")`
- All must approve; fix and re-validate on rejection

### Phase 5 - Cleanup

Delete all state files on successful completion.

- Remove `.omk/state/autopilot-state.json`, `ralph-state.json`, `ultrawork-state.json`, `ultraqa-state.json`
- Run `cancel` skill for clean exit

## Tool Usage

- Use `Agent(subagent_type="architect", ...)` for Phase 4 architecture validation
- Use `Agent(subagent_type="security-reviewer", ...)` for Phase 4 security review
- Use `Agent(subagent_type="code-reviewer", ...)` for Phase 4 quality review
- Use `Agent(subagent_type="analyst", ...)` for requirements analysis in Phase 0
- Use `Agent(subagent_type="critic", ...)` for plan validation in Phase 1
- Use `Shell` for builds, tests, and lint commands
- Never block on external tools; proceed with available agents if delegation fails

## Examples

**Good**: "autopilot A REST API for a bookstore inventory with CRUD operations using TypeScript"
- Specific domain, clear features, technology constraint. Autopilot has enough context.

**Bad**: "fix the bug in the login page"
- Single focused fix, not a multi-phase project. Use direct executor delegation or ralph instead.

## Escalation and Stop Conditions

- Stop and report when the same QA error persists across 3 cycles (fundamental issue requiring human input)
- Stop and report when validation keeps failing after 3 re-validation rounds
- Stop when the user says "stop", "cancel", or "abort"
- If requirements were too vague and expansion produces an unclear spec, offer redirect to `deep-interview` or pause and ask for clarification

## Final Checklist

- [ ] All 5 phases completed (Expansion, Planning, Execution, QA, Validation)
- [ ] All validators approved in Phase 4
- [ ] Tests pass (verified with fresh test run output)
- [ ] Build succeeds (verified with fresh build output)
- [ ] State files cleaned up
- [ ] User informed of completion with summary of what was built
