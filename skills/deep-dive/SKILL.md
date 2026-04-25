---
name: deep-dive
description: 2-stage pipeline — trace (causal investigation) → deep-interview (requirements
  crystallization)
metadata:
  triggers:
  - deep dive
  - deep-dive
---

# Deep Dive

2-stage pipeline: trace (causal investigation) → deep-interview (requirements crystallization) with 3-point injection.

## Use When

- Complex problem with both technical root cause AND unclear requirements
- User says "deep dive" or wants comprehensive analysis
- Debugging a systemic issue that may require requirements clarification

## Steps

1. **Stage 1 — Trace**: Use `trace` skill to investigate the technical root cause
   - Form multiple hypotheses
   - Test each with evidence
   - Document the causal chain

2. **Stage 2 — Deep Interview**: Use `deep-interview` skill to crystallize requirements
   - Based on trace findings, identify what needs to change
   - Interview user for clarifications
   - Produce a concrete spec

3. **3-Point Injection**: Inject three critical insights into the final report:
   - Root cause (from trace)
   - Requirements gap (from interview)
   - Recommended solution path

## Output

Final report saved to `.omk/research/deep-dive-<topic>.md`:

- Executive Summary
- Root Cause Analysis
- Requirements Clarification
- Recommended Solution
- Implementation Plan
- Risks and Mitigations

## Tool Usage

- Use `trace` skill patterns for Stage 1
- Use `deep-interview` skill patterns for Stage 2
- Use `Agent(subagent_type="tracer", ...)` for deep causal analysis
- Use `Agent(subagent_type="analyst", ...)` for requirements analysis
