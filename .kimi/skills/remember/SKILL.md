---
name: remember
description: Review reusable project knowledge and decide what belongs in project memory, notepad, or durable docs
triggers:
  - "remember"
  - "save this"
  - "remember this"
---

# Remember

Review reusable project knowledge and decide what belongs in project memory, notepad, or durable docs.

## Use When

- User wants to persist knowledge from the current session
- User says "remember this" or wants to save findings
- Need to decide where knowledge should live (memory vs docs)

## Decision Tree

| Knowledge Type | Destination | Why |
|----------------|-------------|-----|
| Code patterns, conventions | `.omk/project-memory.json` | Cross-session, structured |
| Session notes, working thoughts | `.omk/notepad.md` | Persistent but informal |
| Architecture decisions | `.omk/wiki/architecture.md` | Durable, referenceable |
| API docs, external refs | `.omk/wiki/<topic>.md` | Long-term knowledge |
| Temporary working notes | Current session only | Ephemeral |

## Steps

1. **Identify knowledge**: What was learned in this session that's worth keeping?
2. **Classify**: Use the decision tree above
3. **Write**: Save to the appropriate location
4. **Cross-reference**: Update indexes and links

## Tool Usage

- Use `ReadFile` to check existing memory
- Use `WriteFile` to save new knowledge
- Use `Glob` to find related entries
