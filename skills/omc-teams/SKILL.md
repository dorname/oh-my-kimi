---
name: omc-teams
description: Deprecated in OMK — use `team` skill instead. Original OMC skill for tmux CLI workers.
triggers:
  - "omc-teams"
---

# OMC Teams (Deprecated in OMK)

> **Note**: This skill is deprecated in OMK. The `team` skill provides the same functionality using Kimi CLI's native `Agent` parallel calls instead of tmux processes.

## Migration

Replace `omc-teams` usage with `team`:

```
# OMC (deprecated)
omc-teams 3:executor "fix TypeScript errors"

# OMK (recommended)
team 3:executor "fix TypeScript errors"
```

## Why Deprecated

Kimi CLI does not support tmux-based worker processes. The `team` skill achieves the same parallel execution through native `Agent` tool calls, which is:
- More lightweight (no tmux dependency)
- Cross-platform (works on Windows, macOS, Linux)
- Simpler to manage (no process lifecycle overhead)

## See Also

- `team` skill — the recommended replacement
