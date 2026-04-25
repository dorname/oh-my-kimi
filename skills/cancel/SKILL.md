---
name: cancel
description: Cancel any active OMK mode (autopilot, ralph, ultrawork, ultraqa, team)
metadata:
  triggers:
  - cancel
  - stop
  - abort
---

# Cancel

Cancel any active OMK execution mode. This clears state files and stops active loops.

## Use When

- All tasks are done and verified: invoke cancel for clean exit
- Work is blocked and cannot proceed: explain the blocker, then invoke cancel
- User says "stop", "cancel", or "abort": invoke cancel immediately

## Do Not Use When

- Work is still incomplete: continue working
- A single subtask failed but others can continue: fix and retry

## Steps

1. Read `.omk/state/` to identify active modes
2. For each active mode:
   - Write state file with `active: false`
   - Clear any mode-specific temporary files
3. Report which modes were cancelled

## State Cleanup

| Mode | State File | Cleanup Action |
|------|------------|----------------|
| autopilot | `.omk/state/autopilot-state.json` | Remove or set active=false |
| ralph | `.omk/state/ralph-state.json` | Remove or set active=false |
| ultrawork | `.omk/state/ultrawork-state.json` | Remove or set active=false |
| ultraqa | `.omk/state/ultraqa-state.json` | Remove or set active=false |
| team | `.omk/state/team-state.json` | Remove or set active=false |
| plan | `.omk/state/plan-state.json` | Remove or set active=false |

## Tool Usage

- Use `ReadFile` to check active modes
- Use `WriteFile` to deactivate state
- Use `Shell` to remove state files if needed
