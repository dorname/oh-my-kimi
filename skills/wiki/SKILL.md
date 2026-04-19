---
name: wiki
description: LLM Wiki — persistent markdown knowledge base that compounds across sessions
triggers:
  - "wiki"
  - "wiki this"
  - "wiki add"
  - "wiki query"
---

# Wiki

Persistent markdown knowledge base that compounds across sessions.

## Use When

- User wants to store knowledge for future sessions
- User says "wiki" or wants to query past knowledge
- Need a project-specific knowledge repository

## Commands

| Command | Action |
|---------|--------|
| `wiki add <topic>` | Add a new wiki entry |
| `wiki query <topic>` | Search existing wiki entries |
| `wiki lint` | Check wiki structure and consistency |

## Storage

Wiki entries are stored in `.omk/wiki/` as markdown files:

```
.omk/wiki/
  ├── index.md          # Wiki index with links
  ├── architecture.md   # Architecture decisions
  ├── patterns.md       # Code patterns and conventions
  ├── troubleshooting.md # Known issues and solutions
  └── <topic>.md        # Individual topic entries
```

## Steps

1. **Add**: Write new knowledge to `.omk/wiki/<topic>.md`
2. **Query**: Use `Glob` to find relevant entries, `ReadFile` to read them
3. **Update**: Append or edit existing entries as knowledge evolves

## Tool Usage

- Use `WriteFile` to add/update entries
- Use `Glob` and `ReadFile` to query
- Use `Grep` to search within entries
