---
name: ralph
description: Self-referential loop until task completion with configurable verification reviewer
triggers:
  - "ralph"
  - "don't stop"
  - "must complete"
  - "finish this"
  - "keep going until done"
---

# Ralph

Ralph is a PRD-driven persistence loop that keeps working on a task until ALL user stories in prd.json have passes: true and are reviewer-verified. It wraps ultrawork's parallel execution with session persistence, automatic retry on failure, structured story tracking, and mandatory verification before completion.

## Use When

- Task requires guaranteed completion with verification (not just "do your best")
- Work may span multiple iterations and needs persistence across retries
- Task benefits from structured PRD-driven execution with reviewer sign-off

## Do Not Use When

- User wants a full autonomous pipeline from idea to code — use `autopilot` instead
- User wants to explore or plan before committing — use `plan` skill instead
- User wants a quick one-shot fix — delegate directly to an executor agent
- User wants manual control over completion — use `ultrawork` directly

## Why This Exists

Complex tasks often fail silently: partial implementations get declared "done", tests get skipped, edge cases get forgotten. Ralph prevents this by:
1. Structuring work into discrete user stories with testable acceptance criteria (prd.json)
2. Iterating story-by-story until each one passes
3. Tracking progress and learnings across iterations (progress.md)
4. Requiring fresh reviewer verification against specific acceptance criteria before completion

## PRD Mode

By default, ralph operates in PRD mode. A scaffold `prd.json` is auto-generated when ralph starts if none exists.

**Startup gate:** Ralph always initializes and validates `prd.json` at startup.

**Deslop opt-out:** If the prompt contains `--no-deslop`, skip the mandatory post-review deslop pass entirely.

**Reviewer selection:** Pass `--critic=architect`, `--critic=critic`, or `--critic=codex` in the Ralph prompt to choose the completion reviewer. `architect` remains the default.

## State Management

Ralph state is stored in `.omk/state/ralph-state.json`:

```json
{
  "active": true,
  "iteration": 1,
  "max_iterations": 10,
  "current_phase": "prd_setup|implement|verify|review",
  "reviewer": "architect",
  "no_deslop": false
}
```

## Execution Policy

- Fire independent agent calls simultaneously — never wait sequentially for independent work
- Use `run_in_background=true` for long operations (installs, builds, test suites)
- Deliver the full implementation: no scope reduction, no partial completion, no deleting tests to make them pass

## Steps

1. **PRD Setup** (first iteration only):
   a. Check if `.omk/prd.json` exists. If yes, read it and proceed to Step 2.
   b. If no `prd.json` exists, generate a scaffold. Write it to `.omk/prd.json`.
   c. **CRITICAL: Refine the scaffold.** The auto-generated PRD has generic acceptance criteria. You MUST replace these with task-specific criteria:
      - Analyze the original task and break it into right-sized user stories
      - Write concrete, verifiable acceptance criteria for each story
      - Order stories by priority (foundational work first, dependent work later)
      - Write the refined `prd.json` back to disk
   d. Initialize `.omk/progress.md` if it doesn't exist.
   e. Write `.omk/state/ralph-state.json` with `active: true`.

2. **Pick next story**: Read `prd.json` and select the highest-priority story with `passes: false`. This is your current focus.

3. **Implement the current story**:
   - Delegate to specialist agents:
     - Simple lookups: `Agent(subagent_type="explore", prompt="...")`
     - Standard work: `Agent(subagent_type="executor", prompt="...")`
     - Complex analysis: `Agent(subagent_type="architect", prompt="...")`
   - If during implementation you discover sub-tasks, add them as new stories to `prd.json`
   - Run long operations in background: Builds, installs, test suites use `run_in_background: true`

4. **Verify the current story's acceptance criteria**:
   a. For EACH acceptance criterion in the story, verify it is met with fresh evidence
   b. Run relevant checks (test, build, lint, typecheck) and read the output
   c. If any criterion is NOT met, continue working — do NOT mark the story as complete

5. **Mark story complete**:
   a. When ALL acceptance criteria are verified, set `passes: true` for this story in `prd.json`
   b. Record progress in `.omk/progress.md`: what was implemented, files changed, learnings
   c. Add any discovered codebase patterns to `.omk/progress.md`

6. **Check PRD completion**:
   a. Read `prd.json` — are ALL stories marked `passes: true`?
   b. If NOT all complete, loop back to Step 2 (pick next story)
   c. If ALL complete, proceed to Step 7 (reviewer verification)

7. **Reviewer verification** (tiered, against acceptance criteria):
   - <5 files, <100 lines with full tests: delegate to `Agent(subagent_type="verifier", prompt="...")`
   - Standard changes: delegate to `Agent(subagent_type="critic", prompt="...")`
   - >20 files or security/architectural changes: delegate to `Agent(subagent_type="architect", prompt="...")`
   - Ralph floor: always at least STANDARD verification, even for small changes
   - The selected reviewer verifies against the SPECIFIC acceptance criteria from prd.json
   - **On APPROVAL: immediately proceed to Step 7.5. Do NOT pause to report the verdict to the user.**

7.5 **Mandatory Deslop Pass** (runs unconditionally after Step 7 approval, unless `--no-deslop`):
   - Read the `ai-slop-cleaner` skill and run its workflow on the files changed during the current Ralph session only.
   - Keep the scope bounded to the Ralph changed-file set.

7.6 **Regression Re-verification**:
   - After the deslop pass, re-run all relevant tests, build, and lint checks.
   - Read the output and confirm the post-deslop regression run actually passes.
   - Only proceed to completion after the post-deslop regression run passes.

8. **On approval**: After Step 7.6 passes, run `cancel` skill to cleanly exit and clean up state files.

9. **On rejection**: Fix the issues raised, re-verify with the same reviewer, then loop back to check if the story needs to be marked incomplete.

## Tool Usage

- Use `Agent(subagent_type="architect", ...)` for architect verification when changes are security-sensitive or architectural
- Use `Agent(subagent_type="critic", ...)` when `--critic=critic`
- Use `Agent(subagent_type="verifier", ...)` for lightweight verification of small changes
- Skip architect consultation for simple feature additions, well-tested changes, or time-critical verification
- Proceed with verification alone — never block on unavailable tools
- Use ReadFile/WriteFile for prd.json and progress.md

## Examples

**Good PRD refinement**:
```json
{
  "stories": [
    {
      "id": "US-001",
      "title": "Add flag detection helpers",
      "acceptanceCriteria": [
        "Legacy --no-prd text is stripped from the Ralph working prompt",
        "TypeScript compiles with no errors (npm run build)"
      ],
      "passes": false
    }
  ]
}
```

**Bad** (generic criteria):
```json
{
  "acceptanceCriteria": ["Implementation is complete", "Code compiles"]
}
```

## Escalation and Stop Conditions

- Stop and report when a fundamental blocker requires user input (missing credentials, unclear requirements, external service down)
- Stop when the user says "stop", "cancel", or "abort" — run `cancel` skill
- Continue working when the system sends continuation signals
- If the selected reviewer rejects verification, fix the issues and re-verify (do not stop)
- If the same issue recurs across 3+ iterations, report it as a potential fundamental problem
- **Do NOT stop after Step 7 approval.** Continue through 7 → 7.5 → 7.6 → 8 in the same turn.

## Final Checklist

- [ ] All prd.json stories have `passes: true`
- [ ] prd.json acceptance criteria are task-specific (not generic boilerplate)
- [ ] All requirements from the original task are met (no scope reduction)
- [ ] Zero pending TODO items
- [ ] Fresh test run output shows all tests pass
- [ ] Fresh build output shows success
- [ ] progress.md records implementation details and learnings
- [ ] Selected reviewer verification passed against specific acceptance criteria
- [ ] ai-slop-cleaner pass completed on changed files (or `--no-deslop` specified)
- [ ] Post-deslop regression tests pass
- [ ] `cancel` skill run for clean state cleanup
