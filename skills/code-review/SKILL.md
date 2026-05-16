---
name: code-review
description: Comprehensive code review with optional architectural impact assessment
metadata:
  triggers:
  - code review
  - review code
  - pr review
---

# Code Review

Comprehensive code review across logic, maintainability, and quality, with optional architectural impact assessment.

## Use When

- User wants a review of code changes or a pull request
- User says "code review", "review code", or "pr review"
- Need to evaluate logic correctness, style, and maintainability
- Suspect a change may have broader design implications

## Do Not Use When

- User wants a security-focused audit — use `security-review` instead
- User wants high-level system design — use `plan` or `architect` instead
- Changes are trivial (single-line fixes, typo corrections) — review directly

## Steps

1. **Explore**: Use `explore` agent to determine the scope of changes
   - Identify modified files and their relationships
   - Understand the codebase context surrounding the changes
   - Check for tests, documentation, and related configuration

2. **Code Review**: Use `code-reviewer` agent for the primary review
   - Evaluate logic correctness and edge cases
   - Check coding standards and style consistency
   - Assess maintainability, naming, and readability
   - Verify test coverage for the changed code
   - Flag any obvious performance issues

3. **Architectural Impact** *(optional)*: Use `architect` agent when changes touch core abstractions
   - Evaluate design impact on existing architecture
   - Assess whether the change aligns with established patterns
   - Identify potential ripple effects or coupling risks
   - Provide a verdict: APPROVE / APPROVE WITH SUGGESTIONS / REQUEST CHANGES

## Output

Review results are returned inline. For significant reviews, summarize findings in a structured format:

- **Summary**: High-level verdict and risk level
- **Critical Issues**: Blockers that must be fixed
- **Suggestions**: Improvements that are recommended but not blocking
- **Architecture Impact** *(if applicable)*: Design implications and trade-offs
- **Action Items**: Concrete next steps for the author

## Tool Usage

- Use `explore` agent to gather context before reviewing
- Use `Agent(subagent_type="code-reviewer", description="Run primary code review", ...)` for the primary review
- Use `Agent(subagent_type="architect", description="Assess design impact", ...)` for design impact assessment
- Use `ReadFile` and `diff` tools to inspect changes line-by-line
