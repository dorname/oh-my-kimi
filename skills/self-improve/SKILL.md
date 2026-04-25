---
name: self-improve
description: Autonomous evolutionary code improvement engine with tournament selection
metadata:
  triggers:
  - self-improve
  - evolve
---

# Self-Improve

Autonomous evolutionary code improvement engine with tournament selection.

## Use When

- User wants systematic code quality improvements
- User says "self-improve" or wants evolutionary refinement
- Codebase needs iterative optimization

## Execution Policy

- Each "generation" produces candidate improvements
- Tournament selection: run tests on candidates, keep the best
- Never break existing functionality
- Document each change with rationale

## Steps

1. **Baseline**: Record current test scores and metrics
2. **Generate candidates**: Create N variant implementations of the target code
3. **Evaluate**: Run tests and benchmarks on each candidate
4. **Select**: Keep the candidate with best test pass + performance
5. **Iterate**: Use the winner as the new baseline, repeat
6. **Converge**: Stop when improvements plateau

## Tool Usage

- Use `Shell` for test and benchmark runs
- Use `ReadFile` and `WriteFile` for code variants
- Delegate to `code-simplifier` agent for candidate generation

## Final Checklist

- [ ] Baseline metrics recorded
- [ ] Each candidate tested
- [ ] Best candidate selected with evidence
- [ ] No regressions in existing tests
