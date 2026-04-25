---
name: mcp-setup
description: Configure external tools and integrations for enhanced agent capabilities
metadata:
  triggers:
  - mcp setup
  - setup tools
---

# MCP Setup

Configure external tools and integrations for enhanced agent capabilities.

## Note

OMK does not use MCP servers (Kimi CLI has its own native tool system). This skill configures external CLI tools that agents can invoke via `Shell`.

## Tools Available

| Tool | CLI Command | When to Use |
|------|-------------|-------------|
| Exa Search | `npx exa-mcp-server` | AI-powered web search (use SearchWeb instead) |
| Context7 | `npx @upstash/context7-mcp` | Official docs lookup (use FetchURL instead) |
| Playwright | `npx @playwright/mcp` | Browser automation |
| ast-grep | `sg` or `ast-grep` | Structural code search |

## Steps

1. Check which tools are already installed: `which ast-grep playwright npx`
2. Install missing tools as needed
3. Update `.omk/config.json` with tool paths
4. Verify each tool works

## Tool Usage

- Use `Shell` for installation and verification
- Use `ReadFile` for config inspection
