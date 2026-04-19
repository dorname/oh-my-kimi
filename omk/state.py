#!/usr/bin/env python3
"""
OMK State Manager

Unified state file management for OMK skills.
Replaces OMC's TypeScript State Manager with a Python implementation
that works with Kimi CLI's Shell tool.

Usage from skills:
    Shell: python3 -c "from omk.state import write_state; write_state('ralph', {...)}"
    Shell: python3 -c "from omk.state import read_state; print(read_state('ralph'))"

Or use the CLI:
    python3 -m omk.state write ralph '{"iteration": 1}'
    python3 -m omk.state read ralph
    python3 -m omk.state clear ralph
    python3 -m omk.state list
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any


DEFAULT_STATE_DIR = Path(".omk/state")


def get_state_dir() -> Path:
    """Get the state directory, creating it if necessary."""
    state_dir = Path(os.environ.get("OMK_STATE_DIR", DEFAULT_STATE_DIR))
    state_dir.mkdir(parents=True, exist_ok=True)
    return state_dir


def get_state_file(mode: str) -> Path:
    """Get the path to a state file for a given mode."""
    return get_state_dir() / f"{mode}-state.json"


def read_state(mode: str) -> dict[str, Any] | None:
    """Read state for a mode. Returns None if not found."""
    path = get_state_file(mode)
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def write_state(mode: str, data: dict[str, Any]) -> None:
    """Write state for a mode atomically."""
    path = get_state_file(mode)
    path.parent.mkdir(parents=True, exist_ok=True)

    # Atomic write: write to temp file, then rename
    temp_path = path.with_suffix(".tmp")
    try:
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())
        temp_path.replace(path)
    except Exception:
        if temp_path.exists():
            temp_path.unlink()
        raise


def clear_state(mode: str) -> bool:
    """Clear state for a mode. Returns True if a file was deleted."""
    path = get_state_file(mode)
    if path.exists():
        path.unlink()
        return True
    return False


def list_states() -> list[str]:
    """List all modes that have state files."""
    state_dir = get_state_dir()
    if not state_dir.exists():
        return []
    modes = []
    for f in state_dir.iterdir():
        if f.is_file() and f.suffix == ".json":
            name = f.stem
            if name.endswith("-state"):
                modes.append(name[:-6])  # Strip '-state' suffix
            else:
                modes.append(name)
    return sorted(modes)


def is_mode_active(mode: str) -> bool:
    """Check if a mode has active state."""
    state = read_state(mode)
    return state is not None and state.get("active", False)


def get_active_modes() -> list[str]:
    """Get all modes that are currently active."""
    active = []
    for mode in list_states():
        if is_mode_active(mode):
            active.append(mode)
    return active


def cli() -> int:
    """Command-line interface for state management."""
    if len(sys.argv) < 2:
        print("Usage: python3 -m omk.state <read|write|clear|list> [mode] [data]")
        return 1

    cmd = sys.argv[1]

    if cmd == "list":
        modes = list_states()
        if modes:
            for m in modes:
                status = "active" if is_mode_active(m) else "inactive"
                print(f"{m}: {status}")
        else:
            print("No state files found.")
        return 0

    if cmd in ("read", "write", "clear"):
        if len(sys.argv) < 3:
            print(f"Usage: python3 -m omk.state {cmd} <mode>")
            return 1
        mode = sys.argv[2]

        if cmd == "read":
            state = read_state(mode)
            if state is not None:
                print(json.dumps(state, indent=2, ensure_ascii=False))
            else:
                print(f"No state found for mode: {mode}")
            return 0

        if cmd == "write":
            if len(sys.argv) < 4:
                print(f"Usage: python3 -m omk.state write {mode} '<json_data>'")
                return 1
            try:
                data = json.loads(sys.argv[3])
            except json.JSONDecodeError as e:
                print(f"Invalid JSON: {e}")
                return 1
            write_state(mode, data)
            print(f"State written for mode: {mode}")
            return 0

        if cmd == "clear":
            cleared = clear_state(mode)
            if cleared:
                print(f"State cleared for mode: {mode}")
            else:
                print(f"No state to clear for mode: {mode}")
            return 0

    print(f"Unknown command: {cmd}")
    print("Usage: python3 -m omk.state <read|write|clear|list> [mode] [data]")
    return 1


if __name__ == "__main__":
    sys.exit(cli())
