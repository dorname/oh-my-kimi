---
name: external-context
description: Invoke parallel document-specialist agents for external web searches
  and documentation lookup
metadata:
  triggers:
  - external context
  - look up docs
  - search docs
---

# External Context

Invoke parallel document-specialist agents for external web searches and documentation lookup.

## Use When

- Working with unfamiliar SDKs, APIs, or frameworks
- Need to check official documentation before implementation
- Resolving version compatibility issues
- Finding the correct API for a task

## Steps

1. **Identify unknowns**: List all external dependencies, SDKs, or APIs that need research
2. **Parallel lookup**: Spawn multiple `document-specialist` agents simultaneously, one per topic
3. **Synthesize**: Combine findings into a coherent summary
4. **Report**: Present key findings with concrete code examples and version info

## Tool Usage

- Use `Agent(subagent_type="document-specialist", ...)` for official doc lookup
- Use `SearchWeb` for broad web searches
- Use `FetchURL` for specific documentation pages

## Example

```
Agent(subagent_type="document-specialist", prompt="Find the official Redis Python client docs. What are the breaking changes in redis-py 5.0?")
Agent(subagent_type="document-specialist", prompt="Check FastAPI docs for background tasks. What's the recommended pattern?")
```
