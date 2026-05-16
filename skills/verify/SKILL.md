---
name: verify
description: Verify that a change really works before you claim completion
metadata:
  triggers:
  - verify
  - verify that
---

# Verify

Verify that a change really works before claiming completion.

> **Canonical Verification Entry Point**: This is the canonical validation Skill. All other Skills should invoke `verify` rather than inlining their own build/test/lint/typecheck checklists.

## Use When

- Before claiming a task is complete
- User explicitly asks for verification
- After making changes that affect multiple files
- When another Skill needs validation (e.g., `autopilot`, `ralph`, `ultraqa`, `team`, `ai-slop-cleaner`)

## Steps

1. **Build check**: Run the project's build command and verify success
2. **Test check**: Run relevant tests and verify they pass
3. **Lint check**: Run linters and verify no new errors
4. **Type check**: Run type checker if applicable
5. **Manual verification**: Check that the change actually solves the stated problem
6. **Regression check**: Verify no existing functionality was broken

## Tool Usage

- Use `Shell` for build, test, lint commands
- Use `ReadFile` to inspect outputs
- Delegate to `verifier` agent for complex verification

## Final Checklist

- [ ] Build passes
- [ ] Tests pass
- [ ] Lint clean
- [ ] Type check clean
- [ ] Change solves the stated problem
- [ ] No regressions in existing functionality
