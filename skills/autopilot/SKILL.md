---
name: autopilot
description: Full autonomous execution from idea to working code
metadata:
  triggers:
  - autopilot
  - auto pilot
  - autonomous
  - build me
  - create me
  - make me
  - full auto
  - handle it all
  - I want a
  - I want an
---

# Autopilot

Autopilot takes a brief product idea and autonomously handles the full lifecycle by orchestrating other OMK Skills. It produces working, verified code from a 2-3 line description.

## Use When

- End-to-end autonomous execution from idea to code
- Multi-phase tasks: planning, coding, testing, validation
- Hands-off execution

## Do Not Use When

- Exploring options — use `plan`
- Single focused change — use `ralph` or direct executor
- Quick fix — use direct executor

## Execution Policy

- Phases are sequential; parallel within phases where possible
- QA: up to 5 cycles; same error 3× → stop and report
- All reviewers must approve; rejections get fixed and re-validated
- Cancel with `cancel` skill at any time
- Stop when the user says "stop", "cancel", or "abort"

## State Management

Autopilot state in `.omk/state/autopilot-state.json`:

```json
{
  "active": true,
  "current_phase": "expansion|planning|execution|qa|validation|cleanup",
  "spec_path": ".omk/plans/autopilot-spec.md",
  "plan_path": ".omk/plans/autopilot-impl.md",
  "qa_cycles": 0,
  "max_qa_cycles": 5,
  "validation_rounds": 0,
  "max_validation_rounds": 3
}
```

Write state at the start of each phase.

## Phases

### Phase 0 - Expansion

- **If `spec.md` does not exist**: Load and execute the `deep-interview` Skill to generate a detailed spec.
- **If ralplan consensus plan exists**: Skip Phase 0 and Phase 1 — jump directly to Phase 2.

**Output**: `.omk/plans/autopilot-spec.md`

### Phase 1 - Planning

- Execute the `plan` Skill (direct mode) to generate the implementation plan.

**Output**: `.omk/plans/autopilot-impl.md`

### Phase 2 - Execution

- Execute the `ultrawork` Skill to complete parallel development.

### Phase 3 - QA

- Execute the `ultraqa` Skill to run the QA cycling workflow.

### Phase 4 - Validation

Multi-perspective review in parallel:

- `Agent(subagent_type="architect", description="Review architecture completeness", prompt="You are the Architect reviewer. Review functional completeness of <changes>")`
- `Agent(subagent_type="security-reviewer", description="Review security vulnerabilities", prompt="You are the Security Reviewer agent. Check for vulnerabilities in <changes>")`
- `Agent(subagent_type="code-reviewer", description="Review code quality", prompt="You are the Code Reviewer agent. Review code quality of <changes>")`

All must approve; fix and re-validate on rejection.

### Phase 5 - Cleanup

- Execute the `cancel` Skill to clean up state and exit cleanly.

## Tool Usage

- Use `Agent(subagent_type="architect", description="Validate architecture", ...)` for Phase 4 architecture validation
- Use `Agent(subagent_type="security-reviewer", description="Review security", ...)` for Phase 4 security review
- Use `Agent(subagent_type="code-reviewer", description="Review code quality", ...)` for Phase 4 quality review
- Use `Shell` for builds, tests, and lint commands
- Never block on external tools

## Verification

Before claiming completion, execute the `verify` Skill to run the canonical validation checklist.
