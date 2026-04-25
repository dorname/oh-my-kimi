---
name: ai-slop-cleaner
description: Clean AI-generated code slop with a regression-safe, deletion-first workflow
metadata:
  triggers:
  - cleanup
  - deslop
  - anti-slop
---

# AI Slop Cleaner

Clean AI-generated code slop with a regression-safe, deletion-first workflow.

## Use When

- After AI-generated code needs quality improvement
- User says "cleanup", "deslop", or "anti-slop"
- Code has unnecessary complexity, duplication, or dead code

## Execution Policy

- Prefer deletion over addition
- Keep behavior identical — refactor, don't rewrite
- Run tests after each change
- If a simplification is risky, skip it

## Steps

1. **Identify slop**: Read the target files and identify:
   - Dead code (unused functions, variables, imports)
   - Unnecessary abstraction layers
   - Over-engineered solutions
   - Duplicated code
   - Poor naming

2. **Plan cleanup**: Write a cleanup plan before modifying code
   - List each issue with location
   - Propose minimal fix
   - Flag risky changes

3. **Execute in passes**:
   - Pass 1: Remove dead code
   - Pass 2: Simplify over-engineered parts
   - Pass 3: Improve naming
   - Pass 4: Extract true duplication (only if it reduces complexity)

4. **Verify**: Run tests after each pass

## Tool Usage

- Use `ReadFile` and `Grep` for code analysis
- Use `WriteFile` and `StrReplaceFile` for changes
- Use `Shell` for test runs

## Final Checklist

- [ ] All tests pass
- [ ] Behavior is identical
- [ ] Code is simpler than before
- [ ] No new dependencies introduced
