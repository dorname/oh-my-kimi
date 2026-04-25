---
name: hud
description: Configure HUD display options (deprecated in OMK — Kimi CLI does not
  support stdin status bars)
metadata:
  triggers:
  - hud
  - status bar
---

# HUD

> **Note**: Kimi CLI does not support stdin status bars (the original OMC HUD's primary mechanism). This skill provides configuration guidance for OMK's alternative status reporting.

## OMK Alternative

Instead of a real-time status bar, OMK provides:

1. **State files**: Check `.omk/state/` for active mode status
2. **Progress files**: Read `.omk/progress.md` for session progress
3. **Notepad**: Read `.omk/notepad.md` for persistent notes

## Quick Status Check

```bash
# List active modes
python3 -m omk.state list

# Read current progress
cat .omk/progress.md

# Check notepad
cat .omk/notepad.md
```

## Tool Usage

- Use `ReadFile` for status inspection
- Use `Shell` for quick status commands
