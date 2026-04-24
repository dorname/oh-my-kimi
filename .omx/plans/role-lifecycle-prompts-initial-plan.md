# Role Lifecycle Prompts Implementation Plan

## Executive Summary

- Add OMK-owned lifecycle visibility through Kimi's documented `SubagentStart` and `SubagentStop` hooks, without modifying `kimi-cli/`.
- Ship a lightweight OMK hook handler and installable hook assets so users can see markers such as `【architect】create` and `【architect】complete` during multi-role workflows.
- Keep the implementation inside OMK surfaces: installer, OMK CLI/runtime helpers, OMK docs, and OMK prompt text as a fallback signal.
- Make hook setup explicit and verifiable instead of silently mutating `~/.kimi/config.toml`; provide a generated snippet, install messaging, and doctor/contract checks.
- Preserve the public OMK agent contract and add verification that lifecycle prompts work for `ralplan`-style Planner -> Architect -> Critic delegation.

## RALPLAN-DR Summary

### Principles

1. Prefer documented Kimi extension points over inferred internals.
2. Keep the solution implementation-only within OMK-owned files.
3. Make lifecycle visibility observable by users, not just model-context-visible.
4. Default to low-friction install and verification, but avoid risky hidden config mutation.
5. Preserve current OMK workflows if hooks are absent or fail open.

### Top Decision Drivers

1. `kimi-cli/` is read-only and out of scope, so the solution must use `--agent-file`, custom subagents, and documented hooks only.
2. Users need to tell whether multi-role collaboration actually happened, so the signal must appear at runtime in a human-discernible way.
3. Kimi hook behavior is beta/fail-open, so the design needs a fallback path and a verification story.

### Viable Options

#### Option A: Prompt-only lifecycle announcements in OMK subagent prompts

Pros:
- Lowest implementation cost.
- No Kimi config changes required.
- Works anywhere OMK subagents already run.

Cons:
- Not a true lifecycle signal; it depends on each subagent choosing to emit the text.
- Harder to guarantee consistent `create` and `complete` markers across all workflows.
- Cannot independently prove that the Kimi Agent tool actually launched a subagent instance.

#### Option B: Hook-driven lifecycle markers with OMK-owned hook handler and opt-in config snippet

Pros:
- Uses documented `SubagentStart`/`SubagentStop` events and `agent_name` context from Kimi docs.
- Produces one centralized implementation for all OMK subagent roles.
- Cleanly separates runtime lifecycle visibility from prompt semantics.

Cons:
- Requires users to enable hooks in Kimi config.
- Hook stdout visibility in the current TUI is not fully guaranteed from docs alone.
- Needs installer/docs/doctor work, not just prompt edits.

#### Option C: Hybrid approach: hook-driven primary path plus prompt-level fallback

Pros:
- Best resilience against hook output ambiguity and fail-open behavior.
- Gives users immediate role-intent cues even before hooks are configured.
- Lets OMK verify both "subagent requested" and "subagent lifecycle observed".

Cons:
- Slightly broader scope than pure hooks.
- Needs careful wording to avoid duplicate/noisy markers.

### Selected Direction

Select **Option C**.

Why:
- Option B is the only path grounded in Kimi's documented lifecycle events (`SubagentStart`/`SubagentStop`) and therefore the only sound primary implementation.
- The snapshot already identifies a real uncertainty: docs confirm hook stdout is added to context, but not that it is always shown in the TUI. The fallback prompt markers cover that gap without relying on `kimi-cli/` internals.
- The hybrid design stays within OMK-owned files and does not require a new dependency.

## Requirements Summary

- Users who install OMK and launch Kimi with the installed OMK root agent via `--agent-file` must have a supported path to see whether OMK created/collaborated with multi-role subagents.
- Runtime lifecycle markers must include create/complete role prompts such as `【architect】create` and `【architect】complete`.
- No `kimi-cli/` source modifications are allowed; `kimi-cli/docs/en` may be used as reference only.
- The implementation must remain inside OMK files only and avoid new dependencies unless unavoidable.
- The install experience must explain hook enablement and verification clearly.
- The plan must preserve OMK's existing Planner -> Architect -> Critic `ralplan` behavior and broader public agent roster.

## Acceptance Criteria

1. OMK ships an OMK-owned lifecycle handler that accepts Kimi hook JSON from stdin and emits standardized markers for `SubagentStart` and `SubagentStop`, including the subagent role name.
2. OMK ships installable hook assets or generated config guidance under OMK-owned paths so users can enable the lifecycle prompts without editing `kimi-cli/` source.
3. `./install.sh` communicates the supported enablement path for lifecycle prompts and points users to a concrete verification command or steps after installation.
4. OMK docs describe:
   - the `--agent-file` launch path,
   - the lifecycle prompt feature,
   - how to enable the hooks,
   - how to verify configured hooks,
   - what fallback behavior exists if hooks are not enabled.
5. `ralplan` execution with Planner -> Architect -> Critic has a documented verification path that demonstrates at least those three role lifecycle markers.
6. Contract/doctor-style checks fail if lifecycle assets/docs drift from the public OMK agent roster or if installer messaging omits the supported hook setup.
7. No implementation changes occur under `kimi-cli/`.

## Implementation Steps

### 1. Add an OMK lifecycle hook handler entry point

Target files:
- [omk/cli.py](/home/kyle/oh-my-kimi/omk/cli.py:16)
- [pyproject.toml](/home/kyle/oh-my-kimi/pyproject.toml:10)
- New OMK-owned Python module, likely `omk/role_lifecycle.py`

Planned work:
- Extend the `omk` CLI beyond `state`, `notifier`, and `updater` to expose a lifecycle-oriented subcommand that reads hook JSON from stdin and prints normalized markers.
- Normalize Kimi hook payloads using the documented `hook_event_name`, `agent_name`, `prompt`, and `response` fields from [hooks.md](/home/kyle/oh-my-kimi/kimi-cli/docs/en/customization/hooks.md:80).
- Map `SubagentStart` -> `【<role>】create` and `SubagentStop` -> `【<role>】complete`.
- Keep output minimal and deterministic so the same handler can be reused by both global and project-local installs.

Acceptance checkpoint:
- A single OMK CLI command can transform sample Kimi `SubagentStart`/`SubagentStop` JSON into the exact lifecycle markers.

### 2. Ship OMK-owned hook assets and config snippet generation

Target files:
- [install.sh](/home/kyle/oh-my-kimi/install.sh:94)
- [install.sh](/home/kyle/oh-my-kimi/install.sh:157)
- [install.sh](/home/kyle/oh-my-kimi/install.sh:263)
- New OMK-owned assets under a path such as `hooks/` or `templates/hooks/`

Planned work:
- Add install-time copying of hook helper assets into the target `.kimi` tree adjacent to installed skills/agents, using the same target resolution pattern already used for skills and agents in `install.sh`.
- Generate or install a reusable TOML snippet for `[[hooks]]` entries matching documented Kimi config shape from [config-files.md](/home/kyle/oh-my-kimi/kimi-cli/docs/en/configuration/config-files.md:206).
- Prefer explicit snippet generation plus install output over silent in-place mutation of `~/.kimi/config.toml`.
- Include two hook registrations:
  - `event = "SubagentStart"` with matcher scoped to OMK public roles.
  - `event = "SubagentStop"` with the same matcher.
- Ensure install messaging tells users where the snippet lives and how to verify with `/hooks`.

Acceptance checkpoint:
- Fresh install places OMK lifecycle hook assets/snippet in the target `.kimi` tree and prints where to enable them.

### 3. Add prompt-level fallback lifecycle guidance in OMK agent prompts

Target files:
- [agents/default/system.md](/home/kyle/oh-my-kimi/agents/default/system.md:37)
- [agents/default/agent.yaml](/home/kyle/oh-my-kimi/agents/default/agent.yaml:29)
- Potentially selected subagent YAMLs if role-specific prompt args are needed

Planned work:
- Update OMK root/system prompt guidance so workflows that delegate subagents explicitly treat lifecycle markers as part of the visible collaboration contract when hooks are absent or uncertain.
- Keep this as fallback behavior, not the primary source of truth, to avoid fighting the hook-based path.
- Scope fallback text to OMK public roles and especially consensus flows already defined in `system.md`.

Acceptance checkpoint:
- The prompt contract explicitly requires visible role markers or equivalent lifecycle acknowledgment when OMK launches Planner/Architect/Critic and hooks are unavailable.

### 4. Document lifecycle setup, verification, and constraints

Target files:
- [README.md](/home/kyle/oh-my-kimi/README.md:15)
- [README.md](/home/kyle/oh-my-kimi/README.md:61)
- [README.md](/home/kyle/oh-my-kimi/README.md:226)
- [README_ZH.md](/home/kyle/oh-my-kimi/README_ZH.md:15)
- Relevant skill docs if install guidance is duplicated there

Planned work:
- Add a short "Role lifecycle prompts" section to the Quick Start / verification path.
- Document the supported startup contract: install OMK, launch Kimi with `--agent-file`, enable OMK lifecycle hooks, verify with `/hooks`, then trigger a known multi-role workflow such as `ralplan`.
- Document that hooks are beta/fail-open per Kimi docs [hooks.md](/home/kyle/oh-my-kimi/kimi-cli/docs/en/customization/hooks.md:190), and that OMK uses a prompt-level fallback.
- Add example transcript snippets using `【architect】create` and `【architect】complete`.

Acceptance checkpoint:
- README and README_ZH each contain an end-to-end lifecycle feature explanation and verification path.

### 5. Extend contract and doctor checks for lifecycle coverage

Target files:
- [scripts/check-agent-contract.py](/home/kyle/oh-my-kimi/scripts/check-agent-contract.py:69)
- Potential existing doctor/setup skills or scripts that validate install state

Planned work:
- Extend the contract checker to validate lifecycle docs/assets against the public registry extracted from [agents/default/agent.yaml](/home/kyle/oh-my-kimi/agents/default/agent.yaml:29).
- Add checks that:
  - lifecycle hook assets exist,
  - installer messaging mentions lifecycle enablement,
  - README includes lifecycle setup and `--agent-file`,
  - hook matcher coverage stays aligned with the OMK public role roster.
- If OMK already has a doctor/setup flow, add a read-only verification command that confirms the lifecycle snippet/hook assets are present and points users to `/hooks`.

Acceptance checkpoint:
- Contract validation fails when lifecycle roster/docs drift and passes when aligned.

### 6. Verify on supported install modes

Target files:
- No new product files beyond verification docs/scripts unless a small helper is needed

Planned work:
- Verify project-local install (`./install.sh --project`) and default/XDG-aware install paths since target resolution is split in [install.sh](/home/kyle/oh-my-kimi/install.sh:94).
- Validate the happy path against documented Kimi custom agent loading via `--agent-file` in [agents.md](/home/kyle/oh-my-kimi/kimi-cli/docs/en/customization/agents.md:23).
- Validate the hook config shape against [config-files.md](/home/kyle/oh-my-kimi/kimi-cli/docs/en/configuration/config-files.md:206) and event names against [hooks.md](/home/kyle/oh-my-kimi/kimi-cli/docs/en/customization/hooks.md:21).

Acceptance checkpoint:
- The feature works in at least project-local and default-install startup flows without changing `kimi-cli/`.

## Risks And Mitigations

### Risk 1: Hook stdout is added to model context but not always visibly rendered to the user

Mitigation:
- Use hook-driven markers as the primary path.
- Add prompt-level fallback lifecycle guidance for consensus/delegation flows.
- Document the fallback clearly so users know what signal to expect.

### Risk 2: Auto-editing `~/.kimi/config.toml` could be brittle or user-hostile

Mitigation:
- Do not silently mutate the user config in the first iteration.
- Generate/install a snippet and print exact next steps from `install.sh`.
- Add doctor/docs support for quick verification.

### Risk 3: Hook matcher drift from OMK's public role roster

Mitigation:
- Reuse the public roster derived from `agents/default/agent.yaml`.
- Extend `scripts/check-agent-contract.py` to validate lifecycle role coverage.

### Risk 4: Duplicate/noisy markers when both hooks and fallback prompts are active

Mitigation:
- Keep fallback scoped and conditional in wording.
- Prefer hook output for exact create/complete markers and make prompt fallback less repetitive.

### Risk 5: Kimi hooks are beta and fail open

Mitigation:
- Avoid making hooks mandatory for workflow correctness.
- Treat hooks as observability only; execution should continue even if they fail.
- Document the beta/fail-open behavior and expected troubleshooting path.

## Verification Steps

1. Unit-level verification for the OMK lifecycle parser/formatter:
   - Pipe fixture JSON representing `SubagentStart` and `SubagentStop` into the new `omk` subcommand.
   - Assert exact output `【architect】create` / `【architect】complete`.

2. Installer verification:
   - Run `./install.sh --dry-run`, `./install.sh --project`, and an XDG-aware install path check.
   - Confirm lifecycle hook assets/snippet are targeted to the same install root family as skills and agents.

3. Contract verification:
   - Run `python3 scripts/check-agent-contract.py`.
   - Confirm lifecycle role coverage and docs/install messaging remain aligned.

4. Manual Kimi verification:
   - Launch with documented path: `kimi --agent-file ./.kimi/agents/agent.yaml` or the installed absolute path.
   - Enable the OMK lifecycle hook snippet in Kimi config.
   - Run `/hooks` and confirm `SubagentStart` and `SubagentStop` hooks are registered.
   - Trigger `ralplan` and observe Planner/Architect/Critic lifecycle markers.

5. Fallback verification:
   - Temporarily disable lifecycle hooks and confirm OMK still emits visible role-collaboration cues in the consensus flow.

## ADR

### Decision

Adopt a hybrid lifecycle-visibility design:
- Primary path: OMK-owned Kimi `SubagentStart`/`SubagentStop` hooks producing `【role】create` and `【role】complete`.
- Secondary path: prompt-level fallback cues in OMK delegation workflows.

### Drivers

1. Need a trustworthy signal that subagents were actually created/collaborated.
2. No `kimi-cli/` source edits are allowed.
3. Kimi's hook system is documented but beta and fail-open.

### Alternatives Considered

- Prompt-only lifecycle text in subagent prompts.
- Hook-only implementation with no fallback.
- Silent install-time mutation of `~/.kimi/config.toml`.

### Why Chosen

- Hook-only is architecturally correct but too exposed to beta/visibility ambiguity.
- Prompt-only is easy but not strong enough evidence of true subagent lifecycle.
- Explicit snippet-based enablement is safer than mutating user config and still keeps setup low-friction.

### Consequences

- OMK gains a small runtime/helper surface and extra installer/docs work.
- Users get a concrete observability feature without waiting on `kimi-cli` changes.
- Some setup remains opt-in because Kimi config is user-owned.

### Follow-ups

1. If Kimi later documents guaranteed user-visible hook output, simplify or reduce prompt fallback.
2. Consider adding an `omk doctor lifecycle` or equivalent install-health check if the initial verification flow proves too manual.
3. Consider optional config merge automation later only if it can be made safe, idempotent, and reversible.

## Available Agent Types Roster

Public OMK roster grounded in [agents/default/agent.yaml](/home/kyle/oh-my-kimi/agents/default/agent.yaml:29):

- `coder`
- `explore`
- `plan`
- `architect`
- `executor`
- `debugger`
- `critic`
- `analyst`
- `designer`
- `writer`
- `verifier`
- `tracer`
- `code-reviewer`
- `security-reviewer`
- `test-engineer`
- `document-specialist`
- `code-simplifier`
- `scientist`

## Follow-up Staffing Guidance

### Ralph path

Recommended when:
- The implementation stays tightly coupled across installer, CLI helper, and docs.
- One owner should sequence the hook handler, installer assets, and verification end to end.

Suggested lane and reasoning:
- `executor` high: implement OMK CLI hook handler, installer assets, docs updates.
- `verifier` high: validate install modes, contract checks, and manual lifecycle evidence.
- `critic` medium: optional final review if the fallback/prompt noise tradeoff remains delicate.

Launch hint:
- `ralph implement .omx/plans/role-lifecycle-prompts-initial-plan.md`

Verification path:
- Ralph should not close until lifecycle hook assets are installed, `/hooks` verification is documented, and a sample `ralplan` flow shows Planner/Architect/Critic markers.

### Team path

Recommended when:
- You want faster parallel execution across independent write scopes.
- The docs/installer/checker work can be split cleanly from OMK CLI helper work.

Suggested staffing:
- Lane 1: `executor` high for `omk/cli.py`, new lifecycle module, hook asset templates.
- Lane 2: `writer` medium for `README.md`, `README_ZH.md`, install/verification docs.
- Lane 3: `verifier` high or `test-engineer` medium for contract checker updates and install verification script/test coverage.
- Optional lane 4: `architect` medium for pre-merge review of the hybrid hook/fallback boundary.

Launch hints:
- `$team implement .omx/plans/role-lifecycle-prompts-initial-plan.md`
- `omx team --plan .omx/plans/role-lifecycle-prompts-initial-plan.md`

Team verification path:
- Re-run contract checks.
- Re-run install dry-run/project-local verification.
- Execute a documented manual Kimi verification using `/hooks` and `ralplan`.
- Capture whether markers appear from hooks, fallback, or both, and keep the final behavior documented.

## Architect Review Focus

Please challenge these points:

1. Whether the hybrid hook-plus-fallback design is the right minimum viable scope.
2. Whether install-time snippet generation is preferable to config auto-merge for first release.
3. Whether lifecycle markers should cover only consensus-critical roles first or the full OMK public roster immediately.
