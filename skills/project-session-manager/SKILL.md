---
name: project-session-manager
description: Worktree-first dev environment manager for issues, PRs, and features
metadata:
  triggers:
  - project session
  - psm
  - worktree
---

# Project Session Manager

Worktree-first development environment manager for issues, PRs, and features.

## Use When

- Starting work on a new issue or feature
- Need isolated git worktrees for parallel development
- User says "project session" or "worktree"

## Steps

1. **Identify task**: Get issue/PR number or feature name from user
2. **Create worktree**: `git worktree add .omk/worktrees/<branch-name>`
3. **Set up environment**: Install dependencies, configure environment
4. **Record session**: Write session info to `.omk/state/sessions/<id>.json`
5. **Activate**: Switch to worktree and begin development

## Session Format

`.omk/state/sessions/<id>.json`:
```json
{
  "id": "feat-auth-123",
  "branch": "feature/auth-improvements",
  "worktree": ".omk/worktrees/feat-auth-123",
  "status": "active|paused|complete",
  "created_at": "2026-04-19T12:00:00Z"
}
```

## Tool Usage

- Use `Shell` for git worktree commands
- Use `WriteFile` for session tracking
- Use `ReadFile` for session retrieval
