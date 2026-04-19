#!/usr/bin/env python3
"""
Check that OMK's public agent contract stays aligned across:
- root agent registry
- README
- system prompt
- omk-reference skill
- installer launch messaging
- shipped Agent(subagent_type="...") calls
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PATH_AWARE_SKILLS = [
    "skills/omk-doctor/SKILL.md",
    "skills/setup/SKILL.md",
    "skills/skill/SKILL.md",
    "skills/learner/SKILL.md",
    "skills/skillify/SKILL.md",
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


def main() -> int:
    agent_yaml = read("agents/default/agent.yaml")
    readme = read("README.md")
    system_md = read("agents/default/system.md")
    reference_skill = read("skills/omk-reference/SKILL.md")
    install_sh = read("install.sh")

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
