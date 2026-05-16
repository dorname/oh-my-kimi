---
name: self-improve
description: Autonomous evolutionary code improvement engine with tournament selection
metadata:
  user-invocable: false
  triggers:
  - self-improve
  - evolve
---

> **INTERNAL MODE DOCUMENT** — This skill is an internal pattern document and is not directly invoked by end users. It is referenced by `autopilot` or `ralph` during optional "optimization rounds".

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
3. **Evaluate**: Run tests and benchmarks on each candidate in parallel

   For each candidate, launch a background evaluation agent:
   ```
   Agent(subagent_type="coder", description="Evaluate candidate 1", prompt="Run all tests and benchmarks on candidate 1. Report: test pass rate, performance metrics, and any regressions.", run_in_background=true)
   Agent(subagent_type="coder", description="Evaluate candidate 2", prompt="Run all tests and benchmarks on candidate 2. Report: test pass rate, performance metrics, and any regressions.", run_in_background=true)
   ...
   ```

   **Concurrency limit**: Start at most 4 candidates in parallel. If there are more than 4 candidates, launch them in batches of 4.

   **Polling**: After launching all candidates in a batch, use `TaskList(active_only=true)` to poll until all background tasks complete.

   **Collection**: Once a batch finishes, use `TaskOutput` to gather results from each evaluation agent. Compare fitness scores (test pass rate + performance) across all candidates.

4. **Select**: Compare fitness scores from all evaluated candidates. Keep the candidate with best test pass + performance.
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
