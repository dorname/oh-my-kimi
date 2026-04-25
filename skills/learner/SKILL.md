---
name: learner
description: Extract a learned skill from the current conversation
metadata:
  triggers:
  - learner
  - extract skill
  - learn from this
---

# Learner

Extract a learned skill from the current conversation and save it for future reuse.

## Use When

- A repeatable workflow has emerged from the conversation
- User says "learner" or wants to capture a pattern
- A successful approach should be reusable in future sessions

## Steps

1. **Identify the pattern**: What workflow, technique, or approach was successful?
2. **Extract the skill**: Write a SKILL.md file capturing:
   - When to use it
   - Step-by-step process
   - Tool usage patterns
   - Examples
3. **Save**: Write to a Kimi-discovered skills directory:
   - `./.kimi/skills/<name>/SKILL.md` for project-local installs
   - `$XDG_CONFIG_HOME/kimi/skills/<name>/SKILL.md` when XDG config is in use
   - `~/.kimi/skills/<name>/SKILL.md` for home-directory installs
4. **Validate**: Ensure the skill is clear, concise, and actionable

## Skill Template

```markdown
---
name: <skill-name>
description: <one-line description>
triggers:
  - "<trigger-word>"
---

# <Skill Name>

## Use When
- <condition 1>
- <condition 2>

## Steps
1. <step 1>
2. <step 2>

## Tool Usage
- Use `<tool>` for <purpose>

## Examples
<good/bad examples>
```

## Tool Usage

- Use `WriteFile` to save the new skill
- Use `ReadFile` to review existing skills for reference
