# Task Statement

Assess whether the current `oh-my-kimi` project is actually usable on the real installed Kimi CLI, and if not, produce a concrete repair plan.

# Desired Outcome

- Establish which advertised OMK capabilities work on current Kimi CLI `1.36.0`.
- Identify concrete compatibility gaps between repo assumptions and official/current Kimi CLI behavior.
- Produce a reviewed fix plan with acceptance criteria and verification steps, without implementing yet.

# Known Facts / Evidence

- OMX session state shows `ralplan` is active for this task.
- The installed CLI is `kimi 1.36.0`.
- `kimi --help` exposes `--agent`, `--agent-file`, `--skills-dir`, `--plan`, `--print`, `login`, `info`, `mcp`, `plugin`, `web`, and other top-level commands.
- Official Kimi CLI docs say custom agents are loaded with `--agent-file`, and built-in agents are `default` and `okabe`.
- Official Kimi CLI docs say skills are auto-discovered from `.kimi/skills`, `.claude/skills`, `.codex/skills`, and generic agent skill dirs.
- `install.sh` installs skills into `.kimi/skills` or `~/.kimi/skills`, and copies agent configs into a sibling `agents` directory.
- `README.md` tells users to run plain `kimi` after install and claims OMK skills/agents will activate naturally.
- `agents/default/agent.yaml` defines OMK routing/system prompt plus custom subagents, but nothing in the installer or README currently wires that file into `kimi --agent-file` or config.
- `README.md` claims 21 specialized agents; `agents/default/agent.yaml` currently enumerates only a subset of those subagents.

# Constraints

- This turn is planning-only (`$ralplan`), not implementation.
- Claims should be grounded in local repo files, the installed Kimi CLI binary, and official Kimi CLI docs.
- If the project is incompatible, the output must be a repair plan saved under `.omx/plans/`.

# Unknowns / Open Questions

- Which OMK features still work if only the skills are installed and the custom agent file is not loaded.
- Whether any undocumented Kimi CLI config path can auto-load the copied agent files.
- Whether the repo should target built-in `default` agent behavior only, or explicitly require a custom `--agent-file` bootstrap path.

# Likely Codebase Touchpoints

- `README.md`
- `install.sh`
- `agents/default/agent.yaml`
- `agents/default/system.md`
- representative subagent files under `agents/default/*.yaml`
- skill docs that promise native `Agent`-based orchestration, such as `skills/team/SKILL.md` and `skills/ralph/SKILL.md`
