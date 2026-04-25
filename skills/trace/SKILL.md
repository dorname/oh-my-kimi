---
name: trace
description: Evidence-driven tracing lane that orchestrates competing tracer hypotheses
metadata:
  triggers:
  - trace
  - trace this
---

# Trace

Evidence-driven tracing that investigates competing hypotheses to find root causes.

## Use When

- Debugging complex, non-obvious issues
- User says "trace" or wants causal investigation
- Production incidents, race conditions, Heisenbugs
- Any problem requiring systematic hypothesis testing

## Execution Policy

- Start with observations, not conclusions
- Form multiple hypotheses before settling on one
- Test each hypothesis with evidence
- Trace backwards from the symptom to the root cause
- Distinguish correlation from causation

## Steps

1. **Observe**: Collect all relevant facts — error messages, logs, recent changes, environment state
2. **Hypothesize**: Form at least 3 competing hypotheses for the root cause
3. **Test**: For each hypothesis, identify what evidence would confirm or refute it
4. **Collect evidence**: Run experiments, read logs, check git history, inspect code
5. **Evaluate**: Score each hypothesis based on evidence strength
6. **Conclude**: Identify the most likely root cause with confidence level
7. **Recommend**: Suggest a fix with clear explanation

## Tool Usage

- Use `Shell` for running experiments and reading logs
- Use `ReadFile` for code inspection
- Use `Grep` for searching patterns across the codebase
- Delegate to `Agent(subagent_type="tracer", ...)` for deep causal analysis

## Output

Trace report saved to `.omk/logs/trace-<timestamp>.md`:

- Observations
- Hypotheses (with evidence for/against)
- Root Cause (with confidence)
- Recommended Fix
- Prevention Measures
