# Test Spec: Kimi CLI 1.36.0 Compatibility Repair

## Objective

Prove that OMK launches through the supported Kimi CLI path and that every retained public role is reachable through a shipped workflow or explicitly removed from the compatibility target.

## Preconditions

- Kimi CLI `1.36.0` is installed.
- OMK repair changes are applied.
- Global, project-local, or `--target-dir` install location is known.

## Verification Matrix

### 1. Installer and docs agree

Checks:

- Compare README quick-start instructions with installer completion output.
- Confirm both describe the same supported launch path and the same capability surface.

Pass if:

- No plain-`kimi` claim remains unless supported and verified.
- Launch command and compatibility notes match exactly.

### 2. Installed agent path is usable

Checks:

- Run installer in `--dry-run`.
- Run installer normally.
- Confirm the documented agent file path exists where the launch instructions expect it.

Pass if:

- The path used in docs/output resolves to a real installed agent file.

### 3. Custom root agent activation proof

Checks:

- Launch Kimi with the supported command, for example:
  `kimi --agent-file <installed-agent.yaml> --print --prompt 'Use Agent(subagent_type="verifier", prompt="Reply READY with your role name") and report success only.'`
- Compare with vanilla Kimi using the same prompt but without `--agent-file`.

Pass if:

- The custom-agent launch succeeds through `verifier`.
- The vanilla launch fails, refuses, or otherwise demonstrates that `verifier` is unavailable there.

### 4. Root-agent roster consistency

Checks:

- Enumerate the retained public roles from docs/reference surfaces.
- Compare them to the root agent registry.

Pass if:

- Every retained public role is registered.
- `planner` vs `plan` is resolved consistently everywhere.
- `qa-tester` and `git-master` are either routed by a shipped workflow or removed from the public compatibility target.

### 5. Workflow smoke tests

Checks:

- `plan` / `ralplan` reaches `planner` or the normalized planning role
- `team` reaches `planner`, `verifier`, `code-reviewer`, `security-reviewer`
- `ralph` reaches `verifier`
- `verify` reaches `verifier`
- `trace` / `deep-dive` reaches `tracer`
- `external-context` reaches `document-specialist`
- `ultraqa` reaches `test-engineer`
- `self-improve` reaches `code-simplifier`
- `sciomk` reaches `scientist`

Pass if:

- Each retained workflow/role pair completes a bounded smoke path without missing-subagent failure.

### 6. Orphan-role policy

Checks:

- Inspect `qa-tester` and `git-master`.

Pass if:

- Each role has a named shipped workflow smoke path, or
- Each role is removed from README, system prompt, reference skill, and compatibility roster.

### 7. Anti-drift automation

Checks:

- Run the consistency check across:
  - `agents/default/agent.yaml`
  - `README.md`
  - `agents/default/system.md`
  - `skills/omk-reference/SKILL.md`
  - `install.sh`
  - shipped `Agent(subagent_type="...")` calls

Pass if:

- The check reports zero drift.

## Exit Criteria

- All matrix items pass.
- No public OMK claim about Kimi `1.36.0` depends on undocumented bootstrap behavior.
- No retained public role lacks either a shipped smoke path or an explicit removal decision.
