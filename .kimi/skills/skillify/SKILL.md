---
name: skillify
description: Turn a repeatable workflow from the current session into a reusable OMK skill draft
triggers:
  - "skillify"
  - "make skill"
---

# Skillify

Turn a repeatable workflow from the current session into a reusable OMK skill draft.

## Use When

- A successful workflow should be reusable
- User says "skillify" or wants to capture a pattern
- Need to create a new skill from recent work

## Steps

1. **Review session**: Identify the successful workflow from the conversation
2. **Extract pattern**: Generalize the workflow beyond the specific task
3. **Write SKILL.md**: Create a skill file with:
   - Frontmatter (name, description, triggers)
   - Purpose
   - Use When / Do Not Use When
   - Steps
   - Tool Usage
   - Examples
4. **Save**: Write to `.kimi/skills/<name>/SKILL.md`
5. **Test**: Verify the skill is clear and actionable

## Tool Usage

- Use `ReadFile` to review conversation history
- Use `WriteFile` to create the skill
