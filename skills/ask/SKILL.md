---
name: ask
description: Process-first advisor routing for Claude, Codex, or Gemini via natural
  language
metadata:
  triggers:
  - ask
  - ask codex
  - ask gemini
---

# Ask

Process-first advisor routing for Claude, Codex, or Gemini.

## Use When

- User wants a specific model's perspective
- User says "ask codex" or "ask gemini"
- Need to route a question to a specific advisor

## Steps

1. **Identify target**: Determine which model/advisor the user wants
2. **Formulate prompt**: Craft a complete, self-contained prompt
3. **Delegate**: Spawn the appropriate agent
4. **Capture**: Record the response as an artifact
5. **Report**: Present the advisor's response to the user

## Routing

| Request | Action |
|---------|--------|
| "ask codex" | Spawn `coder` agent with Codex-style system prompt |
| "ask gemini" | Spawn `architect` agent with Gemini-style system prompt |
| "ask claude" | Use current session (already Claude) |

## Tool Usage

- Use `Agent` for advisor delegation
- Use `WriteFile` to capture artifacts
