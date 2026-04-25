---
name: writer-memory
description: Agentic memory system for writers — track characters, relationships,
  scenes, and themes
metadata:
  triggers:
  - writer memory
  - story memory
---

# Writer Memory

Agentic memory system for writers. Track characters, relationships, scenes, and themes across writing sessions.

## Use When

- Working on fiction, creative writing, or narrative projects
- Need to maintain consistency across long-form writing
- User says "writer memory" or wants story tracking

## Commands

| Command | Action |
|---------|--------|
| `writer-memory init <project>` | Initialize memory for a project |
| `writer-memory char <name>` | Add/update a character |
| `writer-memory rel <a> <b>` | Add/update a relationship |
| `writer-memory scene <title>` | Add/update a scene |
| `writer-memory query <topic>` | Query the memory |

## Storage

Writer memory is stored in `.omk/writer-memory/<project>.json`:

```json
{
  "project": "my-novel",
  "characters": [
    {"name": "Alice", "traits": ["curious", "brave"], "goals": "Find the truth"}
  ],
  "relationships": [
    {"from": "Alice", "to": "Bob", "type": "friend", "status": "strained"}
  ],
  "scenes": [
    {"title": "The Discovery", "characters": ["Alice"], "setting": "Old library"}
  ],
  "themes": ["truth", "betrayal", "redemption"]
}
```

## Tool Usage

- Use `ReadFile` and `WriteFile` for memory I/O
- Use `JSON` parsing for structured queries
