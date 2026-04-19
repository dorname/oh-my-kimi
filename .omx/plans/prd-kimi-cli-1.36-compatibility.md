# PRD: Kimi CLI 1.36.0 Compatibility Repair

## Problem

`oh-my-kimi` is not usable on real Kimi CLI `1.36.0` the way the repo currently advertises it.

- `README.md` and `install.sh` tell users to install and then run plain `kimi`.
- Official Kimi CLI behavior exposes custom agents through `--agent-file`, not through the installer path the repo currently documents.
- `agents/default/agent.yaml` exposes only 10 subagent names, while README, `agents/default/system.md`, and multiple shipped skills depend on a larger roster.

## Goal

Make the project truthful and usable on Kimi CLI `1.36.0` by fixing the bootstrap contract, subagent contract, and workflow contract together.

## Non-Goals

- Do not redesign OMK around built-in Kimi agents only.
- Do not preserve the plain-`kimi` UX through undocumented hacks.
- Do not implement net-new orchestration concepts beyond what is needed to make the current design honest and runnable.

## Users

- Developers who install OMK and expect the README and installer output to match actual Kimi CLI behavior.
- Maintainers who need a repeatable compatibility contract for future Kimi CLI updates.

## User Stories

### US-001 Supported bootstrap

As an installer of OMK, I want the README and installer to tell me the exact supported launch command, so I can start OMK on Kimi CLI `1.36.0` without relying on undocumented behavior.

Acceptance:

- README and installer both document the same supported launch path.
- That launch path is based on `kimi --agent-file <installed-agent.yaml>` unless an official equivalent is implemented and verified.
- Plain `kimi` is no longer advertised as sufficient unless supported and proven.

### US-002 Honest root-agent roster

As an OMK user, I want every publicly documented specialist role to be reachable from the loaded root agent, so workflows do not fail on missing subagent names.

Acceptance:

- Every retained public role is present in the root agent registry.
- The `planner` vs `plan` contract is resolved explicitly.
- `qa-tester` and `git-master` are either given a real workflow path or removed from the public compatibility target.

### US-003 Workflow-role consistency

As an OMK user, I want shipped skills to invoke only roles that actually exist in the compatibility target, so central workflows remain structurally valid.

Acceptance:

- `team` can reach its required planning and verification roles.
- `ralph` and `verify` can reach `verifier`.
- `trace` / `deep-dive` can reach `tracer`.
- `external-context` can reach `document-specialist`.
- `ultraqa` can reach `test-engineer`.
- `self-improve` can reach `code-simplifier`.
- `sciomk` can reach `scientist`.

### US-004 Anti-drift guardrail

As a maintainer, I want an automated consistency check across registry, docs, installer messaging, and skill role references, so the repo does not drift back into unsupported claims.

Acceptance:

- The check covers `agents/default/agent.yaml`, `README.md`, `agents/default/system.md`, `skills/omk-reference/SKILL.md`, `install.sh`, and shipped `Agent(subagent_type="...")` calls.
- The check fails when a documented or referenced role is missing from the compatibility target.

### US-005 Real verification

As a maintainer, I want a concrete Kimi `1.36.0` smoke path, so I can prove OMK is actually loaded and routed through its custom root agent.

Acceptance:

- The verification path includes one custom-only subagent smoke call that distinguishes OMK from vanilla Kimi.
- The verification path includes workflow smoke tests for the retained public roles.

## Workstreams

1. Bootstrap contract repair
2. Root-agent roster reconciliation
3. Skill-role audit and cleanup
4. README and installer messaging repair
5. Compatibility verification and anti-drift automation

## Decision

Use explicit custom-agent bootstrap plus contract reconciliation.

## Alternatives Considered

- Preserve plain `kimi` onboarding via unsupported config or alias tricks
- Downgrade OMK to built-in Kimi roles only

## Why This Choice

It is the smallest truthful path that preserves OMK’s intended multi-agent surface on Kimi CLI `1.36.0`.
