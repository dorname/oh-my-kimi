---
name: deep-interview
description: Socratic deep interview with mathematical ambiguity gating before autonomous
  execution
metadata:
  triggers:
  - deep interview
  - interview me
  - don't assume
  - gather requirements
---

# Deep Interview

Socratic deep interview with ambiguity gating before autonomous execution. Crystallizes vague requirements into concrete, testable specifications.

## Use When

- User has a vague idea and wants to clarify requirements before building
- User says "deep interview", "interview me", "don't assume"
- Task is broad with no specific files, functions, or concrete anchors
- Requirements are unclear and need structured gathering

## Do Not Use When

- User has already provided detailed, specific requirements
- User wants to start coding immediately — use `ralph` or `plan` instead
- Task is a single focused fix with obvious scope

## Execution Policy

- Ask one question at a time — never batch multiple questions
- Gather codebase facts via `explore` agent before asking the user about them
- Each question builds on the previous answer
- Use `AskUserQuestion` for structured preference questions
- Stop interviewing when requirements are clear enough to plan

## Steps

1. **Classify the request**: Determine if it's broad (vague verbs, no specific files, touches 3+ areas)
2. **Ask one focused question** using `AskUserQuestion`
3. **Gather codebase facts first**: Spawn `explore` agent to understand the codebase, then ask informed questions
4. **Build on answers**: Each question builds on the previous
5. **Consult Analyst** for hidden requirements, edge cases, and risks
6. **Create spec** when the user signals readiness

## Output

The deep interview produces a specification saved to `.omk/specs/deep-interview-<topic>.md`:

- Problem Statement
- Requirements (functional and non-functional)
- Constraints and Assumptions
- Acceptance Criteria (testable)
- Out of Scope
- Open Questions (if any)

## Tool Usage

- Use `AskUserQuestion` for all user-facing questions
- Use `explore` agent to gather codebase facts
- Use `analyst` agent for hidden constraint discovery

## Examples

**Good** — Informed question:
```
[explore agent finds: "Auth is in src/auth/ using JWT with passport.js"]
"I see you're using JWT authentication with passport.js.
 For this new feature, should we extend the existing auth or add a separate auth flow?"
```

**Bad** — Asking what could be discovered:
```
"Where is authentication implemented in your codebase?"
```

**Bad** — Batching questions:
```
"What's the scope? And the timeline? And who's the audience?"
```
