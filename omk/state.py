#!/usr/bin/env python3
"""
OMK State Manager — Candidate 1: Enhanced error handling and logging.

Improvements over baseline:
- Structured logging for all operations.
- Granular exception handling (JSONDecodeError, OSError, PermissionError).
- State validation helper.
- Safe file size limits to prevent runaway growth.
"""

from __future__ import annotations

import json
import logging
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

logger = logging.getLogger("omk.state")
if not logger.handlers:
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter("%(levelname)s [omk.state] %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.WARNING)

DEFAULT_STATE_DIR = Path(".omk/state")
MAX_STATE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


def get_state_dir() -> Path:
    """Get the state directory, creating it if necessary."""
    state_dir = Path(os.environ.get("OMK_STATE_DIR", DEFAULT_STATE_DIR))
    try:
        state_dir.mkdir(parents=True, exist_ok=True)
    except PermissionError as exc:
        logger.error("Permission denied creating state dir %s: %s", state_dir, exc)
        raise
    return state_dir


def get_state_file(mode: str) -> Path:
    """Get the path to a state file for a given mode."""
    return get_state_dir() / f"{mode}-state.json"


def read_state(mode: str) -> dict[str, Any] | None:
    """Read state for a mode. Returns None if not found or unreadable."""
    path = get_state_file(mode)
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            logger.warning("State file %s does not contain a JSON object; ignoring.", path)
            return None
        return data
    except json.JSONDecodeError as exc:
        logger.warning("Corrupted JSON in %s: %s", path, exc)
        return None
    except PermissionError as exc:
        logger.error("Permission denied reading %s: %s", path, exc)
        return None
    except OSError as exc:
        logger.error("OS error reading %s: %s", path, exc)
        return None


def write_state(mode: str, data: dict[str, Any]) -> None:
    """Write state for a mode atomically."""
    if not isinstance(data, dict):
        raise TypeError(f"State data must be a dict, got {type(data).__name__}")

    path = get_state_file(mode)
    path.parent.mkdir(parents=True, exist_ok=True)

    payload = json.dumps(data, indent=2, ensure_ascii=False)
    if len(payload.encode("utf-8")) > MAX_STATE_SIZE_BYTES:
        raise ValueError(
            f"State payload for mode '{mode}' exceeds {MAX_STATE_SIZE_BYTES} bytes"
        )

    temp_path = path.with_suffix(".tmp")
    try:
        with open(temp_path, "w", encoding="utf-8") as f:
            f.write(payload)
            f.flush()
            os.fsync(f.fileno())
        temp_path.replace(path)
        logger.debug("State written for mode: %s", mode)
    except PermissionError as exc:
        logger.error("Permission denied writing state for mode %s: %s", mode, exc)
        if temp_path.exists():
            temp_path.unlink()
        raise
    except Exception:
        if temp_path.exists():
            temp_path.unlink()
        raise


def clear_state(mode: str) -> bool:
    """Clear state for a mode. Returns True if a file was deleted."""
    path = get_state_file(mode)
    if path.exists():
        try:
            path.unlink()
            logger.debug("State cleared for mode: %s", mode)
            return True
        except PermissionError as exc:
            logger.error("Permission denied clearing state for mode %s: %s", mode, exc)
            return False
    return False


def list_states() -> list[str]:
    """List all modes that have state files."""
    state_dir = get_state_dir()
    if not state_dir.exists():
        return []
    modes = []
    try:
        for f in state_dir.iterdir():
            if f.is_file() and f.suffix == ".json":
                name = f.stem
                if name.endswith("-state"):
                    modes.append(name[:-6])
                else:
                    modes.append(name)
    except PermissionError as exc:
        logger.error("Permission denied listing state dir: %s", exc)
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


def validate_state(mode: str) -> tuple[bool, str]:
    """Validate that a state's file is readable and well-formed.

    Returns (is_valid, message).
    """
    path = get_state_file(mode)
    if not path.exists():
        return False, f"State file does not exist for mode: {mode}"
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return False, "State data is not a JSON object"
        return True, "Valid"
    except json.JSONDecodeError as exc:
        return False, f"Invalid JSON: {exc}"
    except OSError as exc:
        return False, f"OS error: {exc}"


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
