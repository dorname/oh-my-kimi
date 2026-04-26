"""Unit tests for check-agent-contract.py extractors and validators."""

import importlib.util
import sys
import tempfile
from pathlib import Path

# Load check-agent-contract.py as a module (filename contains hyphen)
_script_path = Path(__file__).resolve().parent.parent / "scripts" / "check-agent-contract.py"
_spec = importlib.util.spec_from_loader("cac", loader=None, origin=str(_script_path))
cac = importlib.util.module_from_spec(_spec)
sys.modules["cac"] = cac
cac.__dict__["__file__"] = str(_script_path)
exec(_script_path.read_text(), cac.__dict__)


# ---------------------------------------------------------------------------
# Agent registry extractors
# ---------------------------------------------------------------------------

SAMPLE_AGENT_YAML = """
  subagents:
    coder:
      path: ./coder.yaml
      description: "Good at general software engineering tasks."
    explore:
      path: ./explore.yaml
      description: "Fast codebase exploration."
"""


def test_extract_registry_agents():
    agents = cac.extract_registry_agents(SAMPLE_AGENT_YAML)
    assert agents == ["coder", "explore"]


def test_extract_table_agents():
    text = "### Build/Analysis\n| `coder` | General |\n| `plan` | Planning |\n\n### Review"
    agents = cac.extract_table_agents(text, "### Build/Analysis", "### Review")
    assert agents == ["coder", "plan"]


def test_extract_system_agents():
    text = "**Build/Analysis Lane:**\n- `coder` — General\n- `plan` — Planning\n\n## Delegation Guidelines"
    agents = cac.extract_system_agents(text)
    assert agents == ["coder", "plan"]


# ---------------------------------------------------------------------------
# Skill reference extractors
# ---------------------------------------------------------------------------

def test_extract_skill_refs():
    text = 'Use Agent(subagent_type="coder") or Agent(subagent_type="plan")'
    refs = cac.extract_skill_refs(text)
    assert refs == ["coder", "plan"]


# ---------------------------------------------------------------------------
# Skill description extractors
# ---------------------------------------------------------------------------

def test_extract_skill_descriptions_from_readme():
    text = (
        "### Workflow Skills\n"
        "| Skill | Trigger | Description |\n"
        "|-------|---------|-------------|\n"
        "| `autopilot` | \"auto\" | Full auto |\n"
        "\n"
        "### Utilities\n"
        "| Skill | Trigger | Description |\n"
        "| `ask` | \"ask\" | Ask things |\n"
        "\n"
        "### Memory & Knowledge\n"
        "| Skill | Trigger | Description |\n"
        "| `wiki` | \"wiki\" | Wiki base |\n"
        "\n"
        "### Deprecated\n"
        "| Skill | Trigger | Description |\n"
        "| `hud` | \"hud\" | Old hud |\n"
        "\n"
        "## Agent Catalog"
    )
    descs = cac.extract_skill_descriptions_from_readme(text)
    assert descs == {
        "autopilot": "Full auto",
        "ask": "Ask things",
        "wiki": "Wiki base",
        "hud": "Old hud",
    }


def test_extract_skill_descriptions_from_frontmatter():
    content = (
        "---\n"
        "name: my-skill\n"
        "description: Does something useful\n"
        "metadata:\n"
        "  triggers:\n"
        "  - something\n"
        "---\n"
        "# My Skill\n"
    )
    with tempfile.NamedTemporaryFile(mode="w", suffix="SKILL.md", delete=False) as f:
        f.write(content)
        f.flush()
        path = Path(f.name)
    try:
        result = cac.extract_skill_descriptions_from_frontmatter(path)
        assert result == {"my-skill": "Does something useful"}
    finally:
        path.unlink()


def test_extract_skill_descriptions_from_frontmatter_multiline():
    content = (
        "---\n"
        "name: multi-line\n"
        "description: Line one\n"
        "  line two\n"
        "metadata:\n"
        "  triggers:\n"
        "  - foo\n"
        "---\n"
    )
    with tempfile.NamedTemporaryFile(mode="w", suffix="SKILL.md", delete=False) as f:
        f.write(content)
        f.flush()
        path = Path(f.name)
    try:
        result = cac.extract_skill_descriptions_from_frontmatter(path)
        assert result == {"multi-line": "Line one line two"}
    finally:
        path.unlink()


# ---------------------------------------------------------------------------
# Substring alignment
# ---------------------------------------------------------------------------

def test_check_substring_alignment_exact():
    assert cac.check_substring_alignment("Hello world", "Hello world")


def test_check_substring_alignment_substring():
    assert cac.check_substring_alignment("Hello world", "Say Hello world today")


def test_check_substring_alignment_three_word_phrase():
    assert cac.check_substring_alignment(
        "Fast codebase exploration", "Fast codebase exploration with search"
    )


def test_check_substring_alignment_fail():
    assert not cac.check_substring_alignment("Completely different phrase", "No overlap here")


def test_check_substring_alignment_period_strip():
    assert cac.check_substring_alignment("Hello world.", "Hello world")


# ---------------------------------------------------------------------------
# Agent description extractors
# ---------------------------------------------------------------------------

def test_extract_agent_descriptions_from_readme():
    text = (
        "### Build/Analysis Lane\n"
        "| Agent | Description | When |\n"
        "| `coder` | General SE | Small work |\n"
        "\n"
        "### Review Lane\n"
        "| Agent | Description | When |\n"
        "| `code-reviewer` | Review | Pre-merge |\n"
        "\n"
        "### Domain Specialists\n"
        "| Agent | Description | When |\n"
        "| `designer` | UI/UX | Frontend |\n"
        "\n"
        "### Coordination\n"
        "| `critic` | Challenge | Before plan |\n"
        "\n"
        "## OMK CLI & State Management"
    )
    descs = cac.extract_agent_descriptions_from_readme(text)
    assert descs == {
        "coder": "General SE",
        "code-reviewer": "Review",
        "designer": "UI/UX",
        "critic": "Challenge",
    }


def test_extract_agent_descriptions_from_system_md():
    text = (
        "**Build/Analysis Lane:**\n"
        "- `coder` — General software engineering\n"
        "- `plan` — Read-only planning\n"
        "\n"
        "## Delegation Guidelines"
    )
    descs = cac.extract_agent_descriptions_from_system_md(text)
    assert descs == {
        "coder": "General software engineering",
        "plan": "Read-only planning",
    }


def test_extract_agent_descriptions_from_reference_skill():
    text = (
        "### Build/Analysis Lane\n"
        "| Agent | Description | When |\n"
        "| `coder` | General SE | Tasks |\n"
        "\n"
        "### Review Lane\n"
        "| Agent | Description | When |\n"
        "| `code-reviewer` | Review | Pre-merge |\n"
        "\n"
        "### Domain Specialists\n"
        "| Agent | Description | When |\n"
        "| `designer` | UI/UX | Frontend |\n"
        "\n"
        "### Coordination\n"
        "| `critic` | Review | Before commit |\n"
        "\n"
        "## Tools"
    )
    descs = cac.extract_agent_descriptions_from_reference_skill(text)
    assert descs == {
        "coder": "General SE",
        "code-reviewer": "Review",
        "designer": "UI/UX",
        "critic": "Review",
    }


# ---------------------------------------------------------------------------
# Shell roster extractors
# ---------------------------------------------------------------------------

def test_extract_public_agents_from_shell():
    text = (
        'public_agents=(\n'
        '    "agent.yaml"\n'
        '    "system.md"\n'
        '    "coder.yaml"\n'
        '    "plan.yaml"\n'
        ')\n'
    )
    agents = cac.extract_public_agents_from_shell(text)
    assert agents == ["coder", "plan"]


def test_extract_non_public_agents_from_shell():
    text = (
        'non_public_agents=(\n'
        '    "git-master.yaml"\n'
        '    "qa-tester.yaml"\n'
        ')\n'
    )
    agents = cac.extract_non_public_agents_from_shell(text)
    assert agents == ["git-master.yaml", "qa-tester.yaml"]


def test_extract_public_agents_from_shell_missing():
    assert cac.extract_public_agents_from_shell("no array here") is None


def test_extract_non_public_agents_from_shell_missing():
    assert cac.extract_non_public_agents_from_shell("no array here") is None



# ---------------------------------------------------------------------------
# YAML validity and skill structure
# ---------------------------------------------------------------------------

def test_check_agent_yaml_validity():
    errors = cac.check_agent_yaml_validity()
    assert errors == [], f"Agent YAML validity errors: {errors}"


def test_check_skill_structure():
    errors = cac.check_skill_structure()
    assert errors == [], f"Skill structure errors: {errors}"

if __name__ == "__main__":
    errors = []
    for name in sorted(dir()):
        if name.startswith("test_"):
            try:
                globals()[name]()
                print(f"  OK {name}")
            except Exception as e:
                errors.append((name, e))
                print(f"  FAIL {name}: {e}")
    if errors:
        print(f"\n{len(errors)} test(s) failed")
        sys.exit(1)
    else:
        print("\nAll tests passed")
