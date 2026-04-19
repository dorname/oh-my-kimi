---
name: deepinit
description: Deep codebase initialization with hierarchical AGENTS.md documentation
triggers:
  - "deepinit"
  - "deep init"
---

# Deepinit

Deep codebase initialization with hierarchical AGENTS.md documentation.

## Use When

- Starting a new project and want comprehensive initialization
- User says "deepinit" or wants deep codebase setup
- Need structured project documentation from day one

## Steps

1. **Analyze project**: Determine project type, language, framework
2. **Create root AGENTS.md**: Write top-level project documentation
3. **Create subdir AGENTS.md files**: Add domain-specific docs to key directories
4. **Initialize structure**: Create standard directories (src/, tests/, docs/)
5. **Add configs**: Create lint, test, build configs appropriate for the stack
6. **Document conventions**: Write coding standards and conventions

## AGENTS.md Hierarchy

```
AGENTS.md              # Root: project overview, setup, conventions
src/AGENTS.md          # Source: architecture, patterns
src/auth/AGENTS.md     # Module: auth-specific docs
tests/AGENTS.md        # Tests: testing strategy
```

## Tool Usage

- Use `WriteFile` for all documentation
- Use `Shell` for directory creation and git init
- Use `Glob` to check existing structure

## Final Checklist

- [ ] Root AGENTS.md created
- [ ] Subdirectory AGENTS.md files created where needed
- [ ] Standard project structure initialized
- [ ] Tool configs added (lint, test, build)
- [ ] Coding conventions documented
- [ ] Git initialized if needed
