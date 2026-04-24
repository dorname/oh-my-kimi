# Role Lifecycle Prompts Context Snapshot

Task statement:
- Optimize this project so users can tell whether Kimi CLI launched multi-role subagents for OMK skills such as `ralplan`.
- Add lifecycle prompts such as `【architect】create` and `【architect】complete`.
- Do not modify `kimi-cli/` source. `kimi-cli/docs/en/` may be used as reference.

Desired outcome:
- After installing OMK and launching Kimi with the OMK agent file, subagent role lifecycle is visible when workflows create and complete roles.
- The solution is implemented in OMK-owned files only and remains compatible with Kimi CLI documented extension points.

Known facts/evidence:
- `install.sh` installs OMK skills to the target `.kimi/skills` path and agent YAML files to the adjacent `.kimi/agents` path.
- `agents/default/agent.yaml` exposes `kimi_cli.tools.agent:Agent` and registers OMK specialist subagents including `plan`, `architect`, and `critic`.
- `skills/ralplan/SKILL.md` requires Planner -> Architect -> Critic delegation through the Agent tool.
- Kimi CLI docs define custom agent files loaded with `kimi --agent-file`.
- Kimi CLI docs define `SubagentStart` and `SubagentStop` hook events with `agent_name`, `prompt`, and `response` context.
- Kimi CLI docs define `[[hooks]]` entries in `~/.kimi/config.toml` and state hook stdout is added to context.

Constraints:
- Do not edit `kimi-cli/` source.
- No new dependencies without explicit request.
- Keep installed behavior compatible with Kimi CLI documented YAML, skill, and hook interfaces.
- Avoid relying on undocumented internals unless protected by a fallback.

Unknowns/open questions:
- Whether hook stdout is visibly printed to the user transcript in the current Kimi TUI, or only added to model context.
- Whether install should auto-merge `~/.kimi/config.toml` hooks, generate an opt-in config snippet, or both.
- Whether lifecycle prompts should cover all subagents or only OMK public specialist roles.

Likely codebase touchpoints:
- `install.sh`: install hook scripts and optionally merge/register hooks.
- `omk/cli.py`: add a lightweight hook subcommand entry point if shell scripts should delegate to Python.
- New OMK-owned hook script under `scripts/` or an installable `.kimi/hooks` template.
- `agents/default/system.md`: strengthen root-agent-visible lifecycle announcements as a fallback.
- `README.md` / `README_ZH.md`: document lifecycle visibility and `/hooks` verification.
- `scripts/check-agent-contract.py`: extend contract checks if role roster or installer expectations change.
