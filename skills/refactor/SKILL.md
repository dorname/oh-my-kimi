---
name: refactor
description: Structured refactoring with design review, parallel implementation, and regression verification
metadata:
  triggers:
  - refactor
  - restructure
  - redesign
---

# Refactor

Structured refactoring workflow with impact analysis, architectural redesign, parallel implementation, and regression verification.

## Use When

- User wants to refactor, restructure, or redesign existing code
- User says "refactor", "restructure", or "redesign"
- Technical debt needs to be addressed across multiple files
- A core abstraction needs to be changed without altering behavior

## Do Not Use When

- User wants to add new features — use `autopilot` or `ralph` instead
- The change is a simple rename or extraction in a single file — do it directly
- User wants to rewrite from scratch without preserving behavior — treat as new implementation

## Steps

1. **Explore (Impact Analysis)**: Use `explore` agent to analyze the refactoring scope
   - Identify all files, functions, and types affected by the change
   - Map dependencies and consumers of the target code
   - Locate existing tests that must continue to pass
   - Document the current state before changes begin

2. **Architect (New Design)**: Use `architect` agent to design the target state
   - Define the new abstraction, interface, or structure
   - Identify migration path from current to target state
   - Assess risks: breaking changes, performance impact, behavioral drift
   - Produce a concrete refactoring plan with file-level steps

3. **Team (Parallel Implementation)**: Use `team` skill to distribute file modifications
   - Break the refactoring into independent or partially-ordered units
   - Delegate units to parallel executor agents
   - Coordinate shared interfaces and crossing changes
   - Merge results and resolve conflicts

4. **Verify (Regression Verification)**: Use `verify` skill to confirm correctness
   - Run the full test suite to detect behavioral drift
   - Perform lint and type checks
   - Review diff to ensure no unintended changes
   - Confirm all acceptance criteria from the architect phase are met

## Output

Refactoring results include:

- **Impact Report**: Files changed, dependencies affected, tests updated
- **Design Summary**: New abstractions and migration rationale
- **Verification Report**: Test results, lint status, and diff summary
- **Rollback Notes**: Steps to revert if issues are discovered post-merge

## Tool Usage

- Use `explore` agent for impact analysis and scope definition
- Use `Agent(subagent_type="architect", description="Redesign and plan refactor", ...)` for redesign and planning
- Use `team` skill for parallel file modifications
- Use `verify` skill for regression testing and validation
- Use `ReadFile` and `WriteFile` / `StrReplaceFile` for edits
- Use `diff` to review changes before finalizing
