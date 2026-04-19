# RALPLAN-DR: Kimi CLI 1.36.0 Compatibility Assessment and Repair Plan

## Verdict

### Concise verdict

The project is **not currently usable as advertised on real Kimi CLI 1.36.0**.

- **Broken by default:** `README.md` tells users to run `./install.sh` and then plain `kimi` with natural OMK keywords, but neither [install.sh](/home/kyle/oh-my-kimi/install.sh:138) nor [README.md](/home/kyle/oh-my-kimi/README.md:22) wires the installed custom root agent into Kimi's documented `--agent-file` entrypoint.
- **Partially recoverable with manual bootstrap:** the repo does install agent YAML files, including [agents/default/agent.yaml](/home/kyle/oh-my-kimi/agents/default/agent.yaml:1), so a user could likely run Kimi with an explicit custom agent file. But even in that mode, the root agent currently exposes only 10 subagent names in [agents/default/agent.yaml](/home/kyle/oh-my-kimi/agents/default/agent.yaml:29), while docs and skills depend on many more.
- **Skill/agent contract is internally inconsistent:** README + system prompt + skills advertise `planner`, `verifier`, `tracer`, `code-reviewer`, `security-reviewer`, `test-engineer`, `qa-tester`, `git-master`, `document-specialist`, `code-simplifier`, and `scientist`, but those names are not registered in the root agent's `subagents` block even though matching YAML files exist under `agents/default/`.

### What currently works vs broken on real Kimi CLI

#### Likely works

- Installing skills into Kimi-discovered skill directories via [install.sh](/home/kyle/oh-my-kimi/install.sh:87) is aligned with the documented skills discovery model.
- The installed custom agent file set is structurally present: [agents/default/agent.yaml](/home/kyle/oh-my-kimi/agents/default/agent.yaml:1) plus matching sibling YAMLs exist.
- If Kimi is launched manually with the installed custom agent file, workflows that only rely on currently exposed subagents are the best candidates to work: `coder`, `explore`, `plan`, `architect`, `executor`, `debugger`, `critic`, `analyst`, `designer`, `writer`.

#### Broken or misleading

- The README "plain `kimi` after install" path is unsupported by current repo wiring: [README.md](/home/kyle/oh-my-kimi/README.md:47), [install.sh](/home/kyle/oh-my-kimi/install.sh:215).
- The advertised "21 specialized agents" claim is false for the actually exposed root agent: [README.md](/home/kyle/oh-my-kimi/README.md:123), [agents/default/agent.yaml](/home/kyle/oh-my-kimi/agents/default/agent.yaml:29).
- `team` depends on `planner`, `verifier`, `code-reviewer`, `security-reviewer`, which are documented in [skills/team/SKILL.md](/home/kyle/oh-my-kimi/skills/team/SKILL.md:55) but not exposed by the root agent.
- `ralph` depends on `verifier` in [skills/ralph/SKILL.md](/home/kyle/oh-my-kimi/skills/ralph/SKILL.md:107), but `verifier` is not exposed.
- Other skills also reference unavailable subagents: `trace`/`deep-dive` -> `tracer`; `verify` -> `verifier`; `external-context` -> `document-specialist`; `ultraqa` -> `test-engineer`; `sciomk` -> `scientist`; `self-improve` -> `code-simplifier`; `autopilot` -> `code-reviewer` and `security-reviewer`; `plan` -> `planner`.

## Requirements Summary

1. Make OMK launch on Kimi through a **documented, supported bootstrap path** rather than assuming plain `kimi` auto-loads the custom root agent.
2. Repair the full contract drift across bootstrap, root-agent registry, skill references, and user-facing docs, rather than treating this as a registry-only fix.
3. Remove or clearly constrain any README/install messaging that promises unsupported behavior.
4. Ensure every shipped skill references only agent names that are actually reachable under the chosen bootstrap.
5. Add a concrete compatibility verification path against installed Kimi CLI 1.36.0.

## Acceptance Criteria

1. Fresh install instructions produce a launch command that uses Kimi's supported custom-agent loading path and does not rely on undocumented auto-loading.
2. The post-repair root agent exposes every agent name referenced by shipped README guidance and shipped skills, or those references are removed/documented as unsupported.
3. Each retained specialist role is not only registered but smoke-routable through at least one dependent workflow that references it.
4. The `planner` naming gap is resolved explicitly, either by aliasing `planner` to the shipped planning agent or by normalizing docs/skills to `plan`.
5. README and installer output give the same startup instructions and same expected capabilities.
6. The repo has an explicit compatibility statement for Kimi CLI `1.36.0` covering what is required to launch OMK successfully.
7. Roles without a shipped dependent workflow smoke path are either:
   - removed from public docs/registry for the Kimi 1.36.0 compatibility target, or
   - paired with a newly added workflow smoke path as part of the repair.
8. A documented verification procedure demonstrates:
   - the custom root agent is loaded,
   - the available subagent roster matches the documented roster,
   - `team`, `ralph`, `trace`, `verify`, `external-context`, `ultraqa`, `self-improve`, and `sciomk` no longer reference missing subagents in their nominal flows.

## Implementation Steps

### 1. Establish the supported bootstrap contract

Files:
- [README.md](/home/kyle/oh-my-kimi/README.md:22)
- [install.sh](/home/kyle/oh-my-kimi/install.sh:1)
- [agents/default/agent.yaml](/home/kyle/oh-my-kimi/agents/default/agent.yaml:1)

Actions:
- Choose an official bootstrap path centered on `kimi --agent-file <installed-agent.yaml>`.
- Update installer behavior to surface that command explicitly after install.
- Decide whether to additionally install a small wrapper/launcher for ergonomics; if so, it must still be a thin wrapper around documented Kimi CLI flags rather than an undocumented config trick.
- Remove the current claim that plain `kimi` is enough after install unless a supported mechanism is implemented and verified.

### 2. Reconcile the exposed root-agent roster with shipped skills/docs

Files:
- [agents/default/agent.yaml](/home/kyle/oh-my-kimi/agents/default/agent.yaml:29)
- [agents/default/system.md](/home/kyle/oh-my-kimi/agents/default/system.md:37)
- [README.md](/home/kyle/oh-my-kimi/README.md:123)

Actions:
- Classify missing roles into:
  - direct-registration roles where a shipped YAML already exists and can be exposed directly, such as `verifier`, `tracer`, `code-reviewer`, `security-reviewer`, `test-engineer`, `qa-tester`, `git-master`, `document-specialist`, `code-simplifier`, and `scientist`;
  - alias-or-rename gaps where the docs/skills say `planner` but the shipped planning agent file is [agents/default/plan.yaml](/home/kyle/oh-my-kimi/agents/default/plan.yaml:1).
- For direct-registration roles, add the missing subagent registrations to the root agent for every existing YAML file that the repo already ships and publicly references.
- For `planner`, choose one explicit contract:
  - alias `planner` to the existing planning agent implementation, or
  - normalize README/system prompt/skills to use `plan` consistently.
- For roles with no shipped workflow smoke path today, decide explicitly whether they are:
  - retained privately but removed from the public compatibility surface until a workflow uses them, or
  - given a new, named workflow smoke path during the repair.
  This decision must cover at least `qa-tester` and `git-master`.
- Cross-check the `system.md` advertised catalog against the actual `subagents` block so the root agent's prompt and runtime surface agree.
- If any shipped agent YAML is not viable on Kimi 1.36.0, remove the claims and rewrite dependent skills instead of leaving dead references.

### 3. Repair the skill contract to match the real runtime

Files:
- [skills/team/SKILL.md](/home/kyle/oh-my-kimi/skills/team/SKILL.md:45)
- [skills/ralph/SKILL.md](/home/kyle/oh-my-kimi/skills/ralph/SKILL.md:68)
- [skills/plan/SKILL.md](/home/kyle/oh-my-kimi/skills/plan/SKILL.md:80)
- [skills/trace/SKILL.md](/home/kyle/oh-my-kimi/skills/trace/SKILL.md:43)
- [skills/deep-dive/SKILL.md](/home/kyle/oh-my-kimi/skills/deep-dive/SKILL.md:51)
- [skills/verify/SKILL.md](/home/kyle/oh-my-kimi/skills/verify/SKILL.md:32)
- [skills/autopilot/SKILL.md](/home/kyle/oh-my-kimi/skills/autopilot/SKILL.md:113)
- [skills/ultraqa/SKILL.md](/home/kyle/oh-my-kimi/skills/ultraqa/SKILL.md:51)
- [skills/external-context/SKILL.md](/home/kyle/oh-my-kimi/skills/external-context/SKILL.md:30)
- [skills/sciomk/SKILL.md](/home/kyle/oh-my-kimi/skills/sciomk/SKILL.md:37)
- [skills/self-improve/SKILL.md](/home/kyle/oh-my-kimi/skills/self-improve/SKILL.md:39)
- [skills/omk-reference/SKILL.md](/home/kyle/oh-my-kimi/skills/omk-reference/SKILL.md:20)

Actions:
- Audit every shipped `Agent(subagent_type="...")` reference against the final roster.
- For each skill, either:
  - keep the agent reference and ensure it is actually registered, or
  - downgrade to an exposed fallback agent and document the reduced behavior, or
  - remove the feature claim if it cannot be made truthful on Kimi 1.36.0.
- Add one explicit “orphan-role” rule: any retained role must name its shipped workflow smoke path.
  Required minimum coverage:
  - `team` -> `planner`/`plan`, `verifier`, `code-reviewer`, `security-reviewer`
  - `ralph` -> `verifier`
  - `trace` / `deep-dive` -> `tracer`
  - `verify` -> `verifier`
  - `external-context` -> `document-specialist`
  - `ultraqa` -> `test-engineer`
  - `self-improve` -> `code-simplifier`
  - `sciomk` -> `scientist`
- For `qa-tester` and `git-master`, either add a named workflow/call site during repair or remove them from the public compatibility roster for Kimi 1.36.0.
- Prioritize `team`, `ralph`, `plan`, `verify`, `autopilot`, `ultraqa`, `self-improve`, and `sciomk` because they are central workflows and/or currently rely on missing names.

### 4. Correct user-facing installation and capability messaging

Files:
- [README.md](/home/kyle/oh-my-kimi/README.md:22)
- [README.md](/home/kyle/oh-my-kimi/README.md:123)
- [install.sh](/home/kyle/oh-my-kimi/install.sh:215)

Actions:
- Rewrite Quick Start / First Use so the startup path is accurate for Kimi 1.36.0.
- Replace unsupported "21 specialized agents" messaging unless the root agent actually exposes all 21.
- Add a short compatibility matrix:
  - plain `kimi`,
  - `kimi --agent-file ...`,
  - built-in subagents only,
  - OMK extended subagents.
- Ensure installer completion output and README tell the same story.

### 5. Add a compatibility verification pass and regression checklist

Files:
- [README.md](/home/kyle/oh-my-kimi/README.md:168)
- [install.sh](/home/kyle/oh-my-kimi/install.sh:215)
- optional new plan/test doc under `.omx/plans/` during execution

Actions:
- Define a repeatable manual verification sequence for Kimi 1.36.0:
  - install globally and/or project-locally,
  - launch via the supported command,
  - confirm the custom root agent is active,
  - exercise representative skills:
    - `ralplan`/`plan` for planning,
    - `team` for verification-stage agent access,
    - `ralph` for `verifier` access,
    - `trace` for `tracer`,
    - `verify` for `verifier`,
    - `external-context` for `document-specialist`.
- Add an automated consistency check that compares:
  - root-agent `subagents` registrations,
  - documented agent roster in `README.md`,
  - installer-emitted launch and capability messaging in [install.sh](/home/kyle/oh-my-kimi/install.sh:215),
  - documented agent roster in `agents/default/system.md`,
  - agent roster in `skills/omk-reference/SKILL.md`,
  - every shipped `Agent(subagent_type="...")` reference across skills.

## Risks and Mitigations

### Risk: unsupported auto-load assumption persists

- **Impact:** users keep following README/install output and silently land on vanilla Kimi behavior.
- **Mitigation:** center all onboarding on explicit `--agent-file`; treat any plain-`kimi` path as unsupported until proven by docs and live verification.

### Risk: adding missing subagent registrations reveals prompt/tool incompatibilities

- **Impact:** the roster becomes larger on paper but some agents still fail at runtime.
- **Mitigation:** verify each added agent name with a minimal smoke path before advertising it broadly; shrink claims if any agent remains non-viable.

### Risk: retained roles have no real workflow entrypoint

- **Impact:** the registry looks complete but some roles remain unreachable in practice.
- **Mitigation:** require every retained role to map to a shipped workflow smoke path, or drop it from the public compatibility target until that path exists.

### Risk: docs are fixed but skills still drift

- **Impact:** user-facing docs become true, but runtime skills still invoke missing names.
- **Mitigation:** perform an exhaustive `Agent(subagent_type=...)` audit during repair and add an automated consistency check rather than relying on checklist discipline alone.

### Risk: preserving plain `kimi` UX drives the project toward unsupported hacks

- **Impact:** fragile bootstrap, future Kimi breakage, harder support burden.
- **Mitigation:** prefer official flags over implicit shell/config hacks; if convenience is needed, provide a transparent wrapper command rather than hidden state.

## Verification Steps

1. Inspect the repaired installer output and README side by side; both must give the same launch command and same capability claims.
2. Run the installer in `--dry-run` and normal mode; confirm the installed agent file location matches the launch instructions.
3. Launch Kimi through the supported command and prove the custom root agent is active with a custom-only smoke prompt, for example:
   - command: `kimi --agent-file <installed-agent.yaml> --print --prompt 'Use Agent(subagent_type=\"verifier\", prompt=\"Reply READY with your role name\") and report success only.'`
   - expected signal: the call succeeds through `verifier`; the same prompt should fail or refuse under vanilla built-in Kimi because `verifier` is not a built-in subagent type.
4. Confirm the root agent's registered subagent names cover every name referenced in shipped skills/docs that remain in the compatibility target.
5. Smoke-test representative workflows:
   - `plan` / `ralplan` can route to `planner` or the normalized documented equivalent,
   - `ralph` can route to `verifier`,
   - `team` can route to `planner`, `verifier`, `code-reviewer`, `security-reviewer`,
   - `trace` / `deep-dive` can route to `tracer`,
   - `verify` can route to `verifier`,
   - `external-context` can route to `document-specialist`,
   - `ultraqa` can route to `test-engineer`,
   - `self-improve` can route to `code-simplifier`,
   - `sciomk` can route to `scientist`.
6. For `qa-tester` and `git-master`, confirm either:
   - a concrete shipped workflow/call site now smoke-routes them, or
   - they were removed from the public compatibility target and no longer appear in README/system prompt/reference skill.
7. Re-run a repo-wide grep for `Agent(subagent_type="...")` and confirm every referenced name exists in the root agent registry or is no longer shipped/documented.
8. Run the automated consistency check and confirm it reports zero drift across installer messaging, root registry, README, system prompt, reference skill, and shipped skill calls.

## RALPLAN-DR Short Summary

### Principles

1. Prefer official Kimi CLI integration points over undocumented behavior.
2. Keep the runtime contract truthful: shipped skills, docs, and agent registry must agree.
3. Preserve OMK's value proposition where viable, but do not over-claim unsupported orchestration.
4. Optimize for supportability: clear bootstrap, reproducible verification, minimal hidden magic.

### Decision Drivers

1. Current onboarding is false on Kimi 1.36.0 because install + plain `kimi` does not load the custom OMK root agent.
2. Core workflows (`team`, `ralph`, `plan`, `verify`, `trace`, `external-context`, `ultraqa`, `self-improve`, `sciomk`) depend on subagent names not currently exposed by the root agent.
3. The repo already ships most of the missing specialist YAML files, so the lowest-risk repair path is to wire them honestly rather than redesign the system around built-ins only.

### Viable Options

#### Option A: Official explicit bootstrap plus contract reconciliation

- **Summary:** require launching Kimi with `--agent-file`, reconcile the root registry with shipped YAMLs, explicitly resolve the `planner`/`plan` naming contract, and align skills/docs with that supported path.
- **Pros:** matches official docs; preserves most OMK value; smallest truthful change; easiest to verify end-to-end.
- **Cons:** gives up the current "just run plain `kimi`" promise unless a wrapper is added; requires an explicit naming decision for `planner`.

#### Option B: Preserve plain-`kimi` UX through implicit config/alias mechanisms

- **Summary:** try to keep the README promise by introducing alias/config/bootstrap magic that makes `kimi` behave like OMK automatically.
- **Pros:** preserves the advertised UX if it works.
- **Cons:** unsupported by current evidence; fragile across Kimi versions; harder to explain and verify; larger support burden.

#### Option C: Retarget OMK to built-in Kimi agents only

- **Summary:** drop the extended roster and rewrite skills/docs around `coder`, `explore`, and `plan` only.
- **Pros:** minimal dependency on custom-agent loading.
- **Cons:** removes a large share of OMK's differentiated functionality; large doc/skill downgrade; does not match project intent.

### Recommended Option

**Option A**. It is the only option that is both evidence-backed and preserves the project's intended multi-agent surface without depending on undocumented Kimi behavior. It should be executed as contract reconciliation, not as blanket registration.

## ADR

### Decision

Adopt an **explicit custom-agent bootstrap** for Kimi CLI 1.36.0 using the documented `--agent-file` path, and reconcile the OMK contract so every shipped skill/doc reference maps to an actually exposed subagent or an explicitly normalized alias.

### Drivers

- Kimi 1.36.0 officially exposes `--agent-file` for custom agents.
- The installer currently installs agent files but does not connect them to Kimi startup.
- The repo already contains YAML definitions for most of the missing specialist subagents, and only the planning role has an obvious naming mismatch (`planner` vs `plan`).

### Alternatives Considered

- Preserve plain `kimi` onboarding with undocumented auto-loading or shell/config tricks.
- Reduce the repo to built-in Kimi agent types and remove the extended orchestration model.

### Why Chosen

This path is the smallest truthful repair. It fixes the broken onboarding contract and the missing-subagent contract without discarding the repo's core design, while explicitly resolving the `planner`/`plan` gap.

### Consequences

- Documentation and installer UX must change.
- Some workflows may still need fallback wording or scope reduction if individual shipped agent YAMLs prove non-viable after exposure.
- Verification becomes a first-class part of installation/support, which is good but adds work.

### Follow-ups

1. Implement the bootstrap and roster fixes.
2. Run a full `Agent(subagent_type=...)` audit across shipped skills.
3. Add a Kimi 1.36.0 compatibility section and smoke-test instructions to the README.
4. Add an automated contract-consistency check covering registry, docs, and skill references.
5. Decide whether to add a convenience wrapper command after the explicit `--agent-file` path is working.

## Available-Agent-Types Roster and Staffing Guidance

### Real current roster on shipped root agent

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

### Shipped-but-not-currently-exposed roster

- `planner` contract name without a dedicated `planner.yaml` file today
- `verifier`
- `tracer`
- `code-reviewer`
- `security-reviewer`
- `test-engineer`
- `qa-tester`
- `git-master`
- `document-specialist`
- `code-simplifier`
- `scientist`

### Target post-repair roster

- `coder`, `explore`, `plan`
- `architect`, `executor`, `debugger`, `critic`, `analyst`, `designer`, `writer`
- `planner` (alias or normalized name for the planning role), `verifier`, `tracer`
- `code-reviewer`, `security-reviewer`
- `test-engineer`, `document-specialist`, `code-simplifier`, `scientist`
- `qa-tester` and `git-master` only if they gain a shipped workflow smoke path during the repair; otherwise remove them from the public compatibility roster for Kimi 1.36.0

### Future staffing guidance: ralph

- **Leader lane:** `architect` or `critic` for final review, medium-to-high reasoning.
- **Execution lane:** `executor`, high reasoning.
- **Lookup lane:** `explore`, low reasoning.
- **Verification lane:** `verifier` for small bounded changes, `critic` for standard review, `architect` for broad/security-sensitive review.
- **Launch hint after plan approval:** use `ralph` only after the bootstrap fix is in place and the `verifier` registration is confirmed live.

### Future staffing guidance: team

- **team-plan:** `explore` + `planner`, low/medium reasoning.
- **team-exec:** `executor` by default; add `debugger` for failures and `designer` only when UI work exists, medium/high reasoning.
- **team-verify:** `verifier` for completion evidence, `code-reviewer` for broad diffs, `security-reviewer` for auth/security scope, medium/high reasoning.
- **team-fix:** `executor` + `debugger`, high reasoning where failure analysis is needed.
- **Launch hint after plan approval:** prefer a team shape only after the full roster is exposed; otherwise `team` will remain structurally underpowered on its verify stage.

### Team verification path

1. Verify the bootstrap first (`--agent-file` path working).
2. Verify `planner` exposure before entering `team-plan`.
3. Verify `verifier`, `code-reviewer`, and `security-reviewer` exposure before claiming `team-verify` is supported.
4. Run one end-to-end team smoke flow on a small harmless task to prove stage routing works before broader rollout.

## Applied Improvements

- Reframed the repair as full contract reconciliation across bootstrap, registry, skills, docs, and installer messaging.
- Added an explicit `planner` vs `plan` contract decision instead of assuming blanket subagent registration is sufficient.
- Tightened acceptance criteria from “registered” to “registered and smoke-routable through a dependent workflow.”
- Added orphan-role handling for `qa-tester` and `git-master` so they cannot remain publicly advertised without a real workflow path.
- Expanded verification to cover `ultraqa -> test-engineer`, `self-improve -> code-simplifier`, and `sciomk -> scientist`.
- Added a concrete custom-root-agent proof step using a custom-only `verifier` smoke prompt.
- Expanded the anti-drift consistency check to include installer-emitted launch messaging.
