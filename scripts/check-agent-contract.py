#!/usr/bin/env python3
"""
Check that OMK's public agent contract stays aligned across:
- root agent registry
- README
- system prompt
- omk-reference skill
- installer launch messaging
- shipped Agent(subagent_type="...") calls
- skill taxonomy and description alignment
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore



ROOT = Path(__file__).resolve().parent.parent
PATH_AWARE_SKILLS = [
    "skills/omk-doctor/SKILL.md",
    "skills/setup/SKILL.md",
    "skills/skill/SKILL.md",
    "skills/learner/SKILL.md",
    "skills/skillify/SKILL.md",
]

CATEGORY_MAP = {
    # Workflow (15)
    "autopilot": "workflow",
    "ralph": "workflow",
    "ultrawork": "workflow",
    "team": "workflow",
    "plan": "workflow",
    "ralplan": "workflow",
    "deep-interview": "workflow",
    "deep-dive": "workflow",
    "ultraqa": "workflow",
    "ai-slop-cleaner": "workflow",
    "visual-verdict": "workflow",
    "trace": "workflow",
    "ccg": "workflow",
    "sciomk": "workflow",
    "self-improve": "workflow",
    # Utility (14)
    "ask": "utility",
    "cancel": "utility",
    "configure-notifications": "utility",
    "debug": "utility",
    "deepinit": "utility",
    "external-context": "utility",
    "mcp-setup": "utility",
    "omk-doctor": "utility",
    "project-session-manager": "utility",
    "release": "utility",
    "setup": "utility",
    "skill": "utility",
    "skillify": "utility",
    "verify": "utility",
    # Memory & Knowledge (5)
    "learner": "memory-knowledge",
    "omk-reference": "memory-knowledge",
    "remember": "memory-knowledge",
    "wiki": "memory-knowledge",
    "writer-memory": "memory-knowledge",
    # Deprecated (2)
    "hud": "deprecated",
    "omk-teams": "deprecated",
}

PUBLIC_AGENTS = [
    "coder",
    "explore",
    "plan",
    "architect",
    "executor",
    "debugger",
    "analyst",
    "verifier",
    "tracer",
    "critic",
    "code-reviewer",
    "security-reviewer",
    "test-engineer",
    "designer",
    "writer",
    "document-specialist",
    "code-simplifier",
    "scientist",
]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def extract_registry_agents(text: str) -> list[str]:
    lines = text.splitlines()
    in_subagents = False
    agents: list[str] = []

    for line in lines:
        if line.startswith("  subagents:"):
            in_subagents = True
            continue
        if in_subagents:
            if not line.startswith("    "):
                break
            match = re.match(r"^    ([a-z0-9-]+):\s*$", line)
            if match:
                agents.append(match.group(1))
    return agents


def extract_table_agents(text: str, start_marker: str, end_marker: str) -> list[str]:
    start = text.index(start_marker)
    end = text.index(end_marker, start)
    block = text[start:end]
    return re.findall(r"\|\s*`([^`]+)`\s*\|", block)


def extract_system_agents(text: str) -> list[str]:
    start = text.index("**Build/Analysis Lane:**")
    end = text.index("## Delegation Guidelines", start)
    block = text[start:end]
    return re.findall(r"- `([^`]+)` —", block)


def extract_skill_refs(text: str) -> list[str]:
    return re.findall(r'Agent\(subagent_type="([^"]+)"', text)


LEGAL_SUBAGENT_TYPES = {"coder", "explore", "plan"}
REQUIRED_EXCLUDE_TOOLS = {
    "kimi_cli.tools.agent:Agent",
    "kimi_cli.tools.ask_user:AskUserQuestion",
    "kimi_cli.tools.plan:ExitPlanMode",
    "kimi_cli.tools.plan.enter:EnterPlanMode",
}




def check_agent_yaml_validity() -> list[str]:
    """Validate that every agent YAML is parseable and references exist."""
    errors: list[str] = []
    agents_dir = ROOT / "agents" / "default"
    if yaml is None:
        errors.append("PyYAML not installed; cannot validate agent YAML syntax.")
        return errors

    for yaml_path in sorted(agents_dir.glob("*.yaml")):
        try:
            data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"{yaml_path.name}: invalid YAML ({exc})")
            continue

        if not isinstance(data, dict) or "agent" not in data:
            errors.append(f"{yaml_path.name}: missing top-level 'agent' key")
            continue

        agent_cfg = data["agent"]
        if not isinstance(agent_cfg, dict):
            continue

        # Check system_prompt_path exists
        sp = agent_cfg.get("system_prompt_path")
        if isinstance(sp, str):
            resolved = yaml_path.parent / sp
            if not resolved.exists():
                errors.append(f"{yaml_path.name}: system_prompt_path '{sp}' not found")

        # Check tools format
        for tool in agent_cfg.get("tools", []):
            if isinstance(tool, str) and ":" in tool:
                continue
            errors.append(f"{yaml_path.name}: invalid tool format '{tool}'")

        # Check exclude_tools format
        for tool in agent_cfg.get("exclude_tools", []):
            if isinstance(tool, str) and ":" in tool:
                continue
            errors.append(f"{yaml_path.name}: invalid exclude_tools format '{tool}'")

        # For root agent, verify subagent paths exist
        if yaml_path.name == "agent.yaml":
            subagents = agent_cfg.get("subagents", {})
            if isinstance(subagents, dict):
                for sub_name, sub_cfg in subagents.items():
                    if isinstance(sub_cfg, dict):
                        sub_path = sub_cfg.get("path")
                        if isinstance(sub_path, str):
                            resolved = yaml_path.parent / sub_path
                            if not resolved.exists():
                                errors.append(
                                    f"agent.yaml: subagent '{sub_name}' path '{sub_path}' not found"
                                )

        # For subagents, verify extend points to agent.yaml
        if yaml_path.name != "agent.yaml":
            extend = agent_cfg.get("extend")
            if isinstance(extend, str):
                resolved = yaml_path.parent / extend
                if not resolved.exists():
                    errors.append(f"{yaml_path.name}: extend '{extend}' not found")
            elif extend is not None:
                errors.append(f"{yaml_path.name}: extend must be a string")

    return errors


def check_skill_structure() -> list[str]:
    """Validate that every skill directory has a valid SKILL.md frontmatter."""
    errors: list[str] = []
    skills_dir = ROOT / "skills"
    for skill_dir in sorted(skills_dir.glob("*/")):
        skill_md = skill_dir / "SKILL.md"
        basename = skill_dir.name
        if not skill_md.exists():
            errors.append(f"skills/{basename}: missing SKILL.md")
            continue

        text = skill_md.read_text(encoding="utf-8")
        if not text.startswith("---"):
            errors.append(f"skills/{basename}: SKILL.md missing YAML frontmatter")
            continue

        name_match = re.search(r"^name:\s*(.+)$", text, re.MULTILINE)
        desc_match = re.search(r"^description:\s*(.+?)(?=^\w|\n---|$)", text, re.MULTILINE | re.DOTALL)

        if not name_match:
            errors.append(f"skills/{basename}: frontmatter missing 'name'")
        else:
            fm_name = name_match.group(1).strip()
            if fm_name != basename:
                errors.append(f"skills/{basename}: frontmatter name '{fm_name}' != directory name")
            if not re.match(r"^[a-z0-9-]+$", fm_name):
                errors.append(f"skills/{basename}: name '{fm_name}' has invalid chars")
            if not (1 <= len(fm_name) <= 64):
                errors.append(f"skills/{basename}: name length {len(fm_name)} out of [1,64]")

        if not desc_match:
            errors.append(f"skills/{basename}: frontmatter missing 'description'")
        else:
            desc = " ".join(desc_match.group(1).split())
            if not (1 <= len(desc) <= 1024):
                errors.append(f"skills/{basename}: description length {len(desc)} out of [1,1024]")

    return errors

def check_agent_yaml_structure() -> list[str]:
    """Validate that every subagent YAML follows Kimi CLI + OMK structural rules."""
    errors: list[str] = []
    agents_dir = ROOT / "agents" / "default"
    for yaml_path in sorted(agents_dir.glob("*.yaml")):
        name = yaml_path.name
        if name == "agent.yaml":
            continue  # root agent has different rules
        text = yaml_path.read_text(encoding="utf-8")

        # Rule: must contain 'extend: ./agent.yaml'
        if "extend: ./agent.yaml" not in text:
            errors.append(f"{name}: missing 'extend: ./agent.yaml'")

        # Rule: must NOT contain 'subagents:' (nesting prohibited)
        if "subagents:" in text:
            errors.append(f"{name}: contains prohibited 'subagents:' key")

        # Rule: non-coordinator roles must exclude Agent, AskUserQuestion, EnterPlanMode, ExitPlanMode
        for tool in REQUIRED_EXCLUDE_TOOLS:
            if tool not in text:
                errors.append(f"{name}: missing exclude_tools entry for {tool}")

    return errors


def check_skill_subagent_refs() -> list[str]:
    """Validate that SKILL.md files only reference legal built-in subagent types."""
    errors: list[str] = []
    for skill_file in sorted((ROOT / "skills").rglob("SKILL.md")):
        text = skill_file.read_text(encoding="utf-8")
        for match in re.finditer(r'Agent\(subagent_type="([^"]+)"', text):
            sub_type = match.group(1)
            if sub_type not in LEGAL_SUBAGENT_TYPES:
                # Compute line number for precise reporting
                line_num = text[: match.start()].count("\n") + 1
                rel_path = skill_file.relative_to(ROOT)
                errors.append(
                    f"{rel_path}:{line_num}: illegal subagent_type='{sub_type}' "
                    f"(must be one of {LEGAL_SUBAGENT_TYPES})"
                )
    return errors


# ---- New helper functions ----


def extract_skill_descriptions_from_readme(text: str) -> dict[str, str]:
    """Parse all four README skill tables and return {skill_name: description}."""
    result: dict[str, str] = {}
    sections = [
        ("### Workflow Skills", "### Utilities"),
        ("### Utilities", "### Memory & Knowledge"),
        ("### Memory & Knowledge", "### Deprecated"),
        ("### Deprecated", "## Agent Catalog"),
    ]
    for start_marker, end_marker in sections:
        try:
            start = text.index(start_marker)
            end = text.index(end_marker, start)
            block = text[start:end]
        except ValueError:
            continue
        for line in block.splitlines():
            parts = line.split("|")
            if len(parts) >= 4:
                m = re.search(r"`([^`]+)`", parts[1])
                if m:
                    name = m.group(1).strip()
                    desc = parts[3].strip()
                    if name and name not in ("Skill", "Agent"):
                        result[name] = desc
    return result


def extract_skill_descriptions_from_frontmatter(path: Path) -> dict[str, str]:
    """Read YAML frontmatter from a SKILL.md and return {name: description}."""
    text = path.read_text(encoding="utf-8")
    name_match = re.search(r"^name:\s*(.+)$", text, re.MULTILINE)
    desc_match = re.search(r"^description:\s*(.+)$", text, re.MULTILINE)
    if not name_match or not desc_match:
        return {}
    name = name_match.group(1).strip()
    lines: list[str] = []
    in_desc = False
    for line in text.splitlines():
        if line.startswith("description:"):
            lines.append(line.split(":", 1)[1].strip())
            in_desc = True
        elif in_desc and (line.startswith("  ") or line.startswith("	")):
            lines.append(line.strip())
        elif in_desc:
            break
    desc = " ".join(lines)
    return {name: desc}


def check_substring_alignment(canonical: str, target: str, ctx: str = "") -> bool:
    """Strip trailing periods, lowercase, and verify substring or 3+ word phrase."""
    c = canonical.rstrip(".").lower()
    t = target.rstrip(".").lower()
    c_words = re.sub(r"[^\w\s]", " ", c).split()
    t_words = re.sub(r"[^\w\s]", " ", t).split()
    c_joined = " ".join(c_words)
    t_joined = " ".join(t_words)
    if c_joined in t_joined or t_joined in c_joined:
        return True
    for i in range(len(c_words) - 2):
        phrase = " ".join(c_words[i : i + 3])
        if phrase in t_joined:
            return True
    for i in range(len(t_words) - 2):
        phrase = " ".join(t_words[i : i + 3])
        if phrase in c_joined:
            return True
    return False


def extract_agent_descriptions_from_readme(text: str) -> dict[str, str]:
    """Extract agent descriptions from README agent catalog tables."""
    result: dict[str, str] = {}
    sections = [
        ("### Build/Analysis Lane", "### Review Lane"),
        ("### Review Lane", "### Domain Specialists"),
        ("### Domain Specialists", "### Coordination"),
        ("### Coordination", "## OMK CLI & State Management"),
    ]
    for start_marker, end_marker in sections:
        try:
            start = text.index(start_marker)
            end = text.index(end_marker, start)
            block = text[start:end]
        except ValueError:
            continue
        for line in block.splitlines():
            m = re.match(r"\|\s*`([^`]+)`\s*\|\s*([^|]+)\|", line)
            if m:
                name = m.group(1).strip()
                desc = m.group(2).strip()
                if name:
                    result[name] = desc
    return result


def extract_agent_descriptions_from_system_md(text: str) -> dict[str, str]:
    """Extract agent descriptions from system.md list format."""
    result: dict[str, str] = {}
    try:
        start = text.index("**Build/Analysis Lane:**")
        end = text.index("## Delegation Guidelines", start)
        block = text[start:end]
    except ValueError:
        return result
    for line in block.splitlines():
        m = re.match(r"- `([^`]+)` — (.+)", line)
        if m:
            name = m.group(1).strip()
            desc = m.group(2).strip()
            if name:
                result[name] = desc
    return result


def extract_agent_descriptions_from_reference_skill(text: str) -> dict[str, str]:
    """Extract agent descriptions from omk-reference skill tables."""
    result: dict[str, str] = {}
    sections = [
        ("### Build/Analysis Lane", "### Review Lane"),
        ("### Review Lane", "### Domain Specialists"),
        ("### Domain Specialists", "### Coordination"),
        ("### Coordination", "## Tools"),
    ]
    for start_marker, end_marker in sections:
        try:
            start = text.index(start_marker)
            end = text.index(end_marker, start)
            block = text[start:end]
        except ValueError:
            continue
        for line in block.splitlines():
            m = re.match(r"\|\s*`([^`]+)`\s*\|\s*([^|]+)\|", line)
            if m:
                name = m.group(1).strip()
                desc = m.group(2).strip()
                if name:
                    result[name] = desc
    return result


def extract_public_agents_from_shell(text: str) -> list[str] | None:
    """Extract agent names (without .yaml suffix) from public_agents array in shell script."""
    match = re.search(r"public_agents=\((.*?)\)", text, re.DOTALL)
    if not match:
        return None
    items = re.findall(r'"([^"]+)"', match.group(1))
    return [item.replace(".yaml", "") for item in items if item not in ("agent.yaml", "system.md")]


def extract_non_public_agents_from_shell(text: str) -> list[str] | None:
    """Extract non_public_agents array from shell script."""
    match = re.search(r"non_public_agents=\((.*?)\)", text, re.DOTALL)
    if not match:
        return None
    return re.findall(r'"([^"]+)"', match.group(1))


def main() -> int:
    agent_yaml = read("agents/default/agent.yaml")
    readme = read("README.md")
    system_md = read("agents/default/system.md")
    reference_skill = read("skills/omk-reference/SKILL.md")
    install_sh = read("install.sh")
    uninstall_sh = read("uninstall.sh")

    registry = sorted(extract_registry_agents(agent_yaml))
    readme_agents = sorted(
        extract_table_agents(
            readme,
            "### Build/Analysis Lane",
            "## OMK CLI & State Management",
        )
    )
    system_agents = sorted(extract_system_agents(system_md))
    reference_agents = sorted(
        extract_table_agents(
            reference_skill,
            "### Build/Analysis Lane",
            "## Tools",
        )
    )

    skill_refs: set[str] = set()
    for skill_file in (ROOT / "skills").rglob("SKILL.md"):
        skill_refs.update(extract_skill_refs(skill_file.read_text(encoding="utf-8")))
    skill_ref_list = sorted(skill_refs)

    errors: list[str] = []

    if registry != readme_agents:
        errors.append(
            "README agent catalog drift:\n"
            f"  registry={registry}\n"
            f"  readme={readme_agents}"
        )
    if registry != system_agents:
        errors.append(
            "System prompt agent catalog drift:\n"
            f"  registry={registry}\n"
            f"  system={system_agents}"
        )
    if registry != reference_agents:
        errors.append(
            "omk-reference agent catalog drift:\n"
            f"  registry={registry}\n"
            f"  omk-reference={reference_agents}"
        )

    missing_from_registry = sorted(ref for ref in skill_ref_list if ref not in registry)
    if missing_from_registry:
        errors.append(
            "Shipped skills reference missing subagent types:\n"
            f"  missing={missing_from_registry}"
        )

    # --- Agent YAML structural validation ---
    yaml_errors = check_agent_yaml_structure()
    if yaml_errors:
        errors.append("Agent YAML structure violations:\n  " + "\n  ".join(yaml_errors))

    # --- Skill subagent_type reference validation ---
    subagent_errors = check_skill_subagent_refs()
    if subagent_errors:
        errors.append("Illegal subagent_type references in skills:\n  " + "\n  ".join(subagent_errors))

    if "--agent-file" not in install_sh:
        errors.append("install.sh does not emit a supported --agent-file launch command.")
    if "Run 'kimi' to start a session" in install_sh:
        errors.append("install.sh still tells users to start plain 'kimi'.")
    if "--agent-file" not in readme:
        errors.append("README does not document the supported --agent-file launch path.")
    if "Start a Kimi CLI session and use skills naturally via keywords:" in readme:
        errors.append("README still implies that plain 'kimi' is the OMK startup path.")

    for skill_path in PATH_AWARE_SKILLS:
        skill_text = read(skill_path)
        if "XDG_CONFIG_HOME" not in skill_text:
            errors.append(f"{skill_path} is missing XDG-aware install guidance.")
        if ".kimi/skills" not in skill_text:
            errors.append(f"{skill_path} is missing project-local skills-directory guidance.")

    # ---- Agent description alignment ----
    agent_yaml_descs: dict[str, str] = {}
    for m in re.finditer(
        r'^    ([a-z0-9-]+):\s*\n      path: .+\n      description: "([^"]+)"',
        agent_yaml,
        re.MULTILINE,
    ):
        agent_yaml_descs[m.group(1)] = m.group(2)

    readme_agent_descs = extract_agent_descriptions_from_readme(readme)
    system_agent_descs = extract_agent_descriptions_from_system_md(system_md)
    reference_agent_descs = extract_agent_descriptions_from_reference_skill(reference_skill)

    for name, canon in agent_yaml_descs.items():
        for source, label in [
            (readme_agent_descs, "README"),
            (system_agent_descs, "system.md"),
            (reference_agent_descs, "omk-reference"),
        ]:
            if name not in source:
                errors.append(f"{label} agent catalog missing {name}")
                continue
            if not check_substring_alignment(canon, source[name], f"{label} {name}"):
                errors.append(
                    f"{label} agent '{name}' description drift: "
                    f"'{source[name]}' does not align with canonical '{canon}'"
                )

    # ---- Skill description alignment ----
    readme_skill_descs = extract_skill_descriptions_from_readme(readme)
    for skill_path in sorted((ROOT / "skills").rglob("SKILL.md")):
        name = skill_path.parent.name
        if CATEGORY_MAP.get(name) == "deprecated":
            continue
        fm = extract_skill_descriptions_from_frontmatter(skill_path)
        if not fm:
            errors.append(f"{name}: could not extract frontmatter description")
            continue
        canon = list(fm.values())[0]
        if name not in readme_skill_descs:
            errors.append(f"README skill table missing {name}")
            continue
        if not check_substring_alignment(canon, readme_skill_descs[name], f"README {name}"):
            errors.append(
                f"README skill '{name}' description drift: "
                f"'{readme_skill_descs[name]}' does not align with frontmatter '{canon}'"
            )

    # ---- Taxonomy validation ----
    counts: dict[str, int] = {}
    for cat in CATEGORY_MAP.values():
        counts[cat] = counts.get(cat, 0) + 1
    expected = {"workflow": 15, "utility": 14, "memory-knowledge": 5, "deprecated": 2}
    for cat, expected_count in expected.items():
        actual = counts.get(cat, 0)
        if actual != expected_count:
            errors.append(f"Taxonomy count mismatch for {cat}: expected {expected_count}, got {actual}")
    if len(CATEGORY_MAP) != 36:
        errors.append(f"CATEGORY_MAP size mismatch: expected 36, got {len(CATEGORY_MAP)}")

    # ---- Deprecated validation ----
    deprecated_in_system_md = []
    for line in system_md.splitlines():
        if line.startswith('| "'):
            m = re.search(r"\|\s*`([^`]+)`\s*\|", line)
            if m and m.group(1) in ("hud", "omk-teams"):
                deprecated_in_system_md.append(m.group(1))
    if deprecated_in_system_md:
        errors.append(
            f"Deprecated skills found in system.md trigger table: {deprecated_in_system_md}"
        )

    readme_deprecated = []
    try:
        dep_start = readme.index("### Deprecated")
        dep_end = readme.index("## Agent Catalog", dep_start)
        dep_block = readme[dep_start:dep_end]
        for line in dep_block.splitlines():
            m = re.search(r"`([^`]+)`", line)
            if m:
                readme_deprecated.append(m.group(1))
    except ValueError:
        errors.append("README missing Deprecated section")
    for dep in ("hud", "omk-teams"):
        if dep not in readme_deprecated:
            errors.append(f"README Deprecated table missing {dep}")

    # ---- install.sh / uninstall.sh roster validation ----
    for sh_name, sh_text in [("install.sh", install_sh), ("uninstall.sh", uninstall_sh)]:
        pub = extract_public_agents_from_shell(sh_text)
        non_pub = extract_non_public_agents_from_shell(sh_text)
        if pub is None:
            errors.append(f"{sh_name}: missing public_agents array")
        elif sorted(pub) != sorted(PUBLIC_AGENTS):
            errors.append(
                f"{sh_name} public_agents drift:\n"
                f"  expected={sorted(PUBLIC_AGENTS)}\n"
                f"  actual={sorted(pub)}"
            )
        if non_pub is None:
            errors.append(f"{sh_name}: missing non_public_agents array")
        elif sorted(non_pub) != ["git-master.yaml", "qa-tester.yaml"]:
            errors.append(
                f"{sh_name} non_public_agents drift:\n"
                f"  expected=['git-master.yaml', 'qa-tester.yaml']\n"
                f"  actual={non_pub}"
            )

    if errors:
        print("OMK agent contract check failed.\n")
        for error in errors:
            print(f"- {error}\n")
        return 1

    print("OMK agent contract check passed.")
    print(f"Registry/public roster: {', '.join(registry)}")
    print(f"Referenced subagent types: {', '.join(skill_ref_list)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
