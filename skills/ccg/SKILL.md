---
name: ccg
description: Claude-Codex-Gemini tri-model orchestration via parallel agent calls,
  then synthesize results
metadata:
  triggers:
  - ccg
  - tri-model
---

# CCG (Claude-Codex-Gemini)

Tri-model orchestration: spawn parallel advisor agents, then synthesize results.

## Use When

- User wants multiple perspectives on a problem
- User says "ccg" or wants tri-model analysis
- Need to compare approaches from different models

## Steps

1. **Define the question**: Clearly state what needs analysis
2. **Spawn parallel agents**: Launch 2-3 agents with the same prompt
   - `Agent(subagent_type="architect", prompt="<question>")`
   - `Agent(subagent_type="critic", prompt="<question>")`
   - `Agent(subagent_type="analyst", prompt="<question>")`
3. **Collect responses**: Gather all agent outputs
4. **Synthesize**: Compare perspectives, identify agreements and disagreements
5. **Recommend**: Present the synthesized conclusion with confidence level

## Tool Usage

- Use `Agent` for parallel advisor calls
- Use `AskUserQuestion` to let user choose between competing recommendations

## Output Format

```
## Synthesis Report

### Agent 1 (Architect) — Key Points
- <point 1>
- <point 2>

### Agent 2 (Critic) — Key Points
- <point 1>
- <point 2>

### Consensus
- <agreed-upon points>

### Dissent
- <areas of disagreement>

### Recommendation
<final synthesized recommendation>
```
