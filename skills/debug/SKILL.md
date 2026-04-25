---
name: debug
description: Diagnose the current OMK session or repo state using logs, traces, state,
  and focused reproduction
metadata:
  triggers:
  - debug
  - diagnose
---

# Debug

Diagnose the current session or repository state using logs, traces, state files, and focused reproduction.

## Use When

- Something is not working as expected
- User says "debug", "diagnose", or "what's wrong?"
- A skill or agent failed unexpectedly
- Need to investigate system state

## Steps

1. **Gather state**: Read `.omk/state/` files to check active modes
2. **Check logs**: Read `.omk/logs/` for recent errors or traces
3. **Inspect environment**: Run `env | grep OMK` or check relevant config files
4. **Reproduce**: Attempt to reproduce the issue in isolation
5. **Report**: Provide clear diagnosis with evidence and recommended fix

## Tool Usage

- Use `ReadFile` for state and log inspection
- Use `Shell` for environment checks and reproduction
- Use `Glob` to find relevant files
