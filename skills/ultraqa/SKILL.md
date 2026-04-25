---
name: ultraqa
description: QA cycling workflow — test, verify, fix, repeat until goal met
metadata:
  triggers:
  - ultraqa
  - qa cycle
---

# UltraQA

QA cycling workflow: test, verify, fix, repeat until goal met.

## Use When

- User wants to ensure quality through repeated test-verify-fix cycles
- Task involves complex changes that need iterative validation
- User says "ultraqa" or wants systematic QA

## Execution Policy

- Cycle up to 5 times; if the same error persists 3 times, stop and report
- Each cycle must include fresh test runs, not just "looks good"
- Fix one issue at a time; don't batch unrelated fixes

## Steps

1. **Run tests**: Execute the test suite and collect failures
2. **Analyze failures**: Categorize failures (regression, new bug, test issue, expected change)
3. **Fix highest priority**: Address the most critical failure first
4. **Re-run tests**: Verify the fix and check for new issues
5. **Repeat**: Continue until all tests pass or max cycles reached

## State Management

UltraQA state in `.omk/state/ultraqa-state.json`:

```json
{
  "active": true,
  "cycle": 1,
  "max_cycles": 5,
  "same_error_count": 0,
  "last_error": ""
}
```

## Tool Usage

- Use `Shell` for test/build commands
- Use `ReadFile` to inspect test output
- Delegate to `test-engineer` agent for test strategy

## Final Checklist

- [ ] All tests pass
- [ ] Build succeeds
- [ ] Lint clean
- [ ] No recurring errors across cycles
