---
name: sciomk
description: Orchestrate parallel scientist agents for comprehensive analysis with
  AUTO mode
metadata:
  triggers:
  - sciomk
  - scientist team
---

# SciOMK

Orchestrate parallel scientist agents for comprehensive analysis.

## Use When

- Complex data analysis requiring multiple analytical angles
- User says "sciomk" or wants scientific analysis
- Need statistical rigor and comprehensive research

## Steps

1. **Define research goal**: Clearly state the hypothesis or question
2. **Decompose analysis**: Break into independent analytical tasks
3. **Spawn scientists**: Launch parallel `scientist` agents with different analytical focuses
4. **Collect findings**: Gather all agent reports
5. **Synthesize**: Combine findings into a coherent research report
6. **Validate**: Check statistical soundness and methodology

## AUTO Mode

When `AUTO` is specified, SciOMK automatically:
- Determines the optimal number of scientist agents
- Selects analytical approaches based on data type
- Generates visualizations where helpful

## Tool Usage

- Use `Agent(subagent_type="scientist", ...)` for parallel analysis
- Use `Shell` for data processing and visualization
- Use `WriteFile` for research report

## Output

Research report saved to `.omk/research/sciomk-<topic>.md`:

- Research Question
- Methodology
- Findings (per agent)
- Synthesis
- Conclusions
- Limitations
- Recommendations
