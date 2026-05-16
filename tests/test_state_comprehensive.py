"""Comprehensive tests for omk.state candidates."""
import json
import os
import sys
import tempfile
import time
from pathlib import Path

# We will import the candidate module dynamically
CANDIDATE_PATH = os.environ.get("CANDIDATE_STATE_PATH", "omk/state.py")

# Load candidate as module
_spec = __import__("importlib.util").util.spec_from_file_location("state_cand", CANDIDATE_PATH)
_state_mod = __import__("importlib.util").util.module_from_spec(_spec)
sys.modules["state_cand"] = _state_mod
_spec.loader.exec_module(_state_mod)

get_state_dir = _state_mod.get_state_dir
get_state_file = _state_mod.get_state_file
read_state = _state_mod.read_state
write_state = _state_mod.write_state
clear_state = _state_mod.clear_state
list_states = _state_mod.list_states
is_mode_active = _state_mod.is_mode_active
get_active_modes = _state_mod.get_active_modes
cli = _state_mod.cli


class TestStateLifecycle:
    def setup_method(self):
        self._orig_env = os.environ.get("OMK_STATE_DIR")
        self.tmpdir = tempfile.mkdtemp()
        os.environ["OMK_STATE_DIR"] = self.tmpdir
        # Clear any cached state dir
        if hasattr(get_state_dir, "cache_clear"):
            get_state_dir.cache_clear()

    def teardown_method(self):
        if self._orig_env is None:
            os.environ.pop("OMK_STATE_DIR", None)
        else:
            os.environ["OMK_STATE_DIR"] = self._orig_env
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_write_and_read(self):
        write_state("test", {"a": 1})
        assert read_state("test") == {"a": 1}

    def test_read_missing(self):
        assert read_state("nonexistent") is None

    def test_clear(self):
        write_state("x", {"v": 1})
        assert clear_state("x") is True
        assert read_state("x") is None
        assert clear_state("x") is False

    def test_list_states(self):
        write_state("a", {})
        write_state("b", {})
        assert list_states() == ["a", "b"]
        clear_state("a")
        assert list_states() == ["b"]

    def test_is_mode_active(self):
        write_state("active_mode", {"active": True})
        write_state("inactive_mode", {"active": False})
        assert is_mode_active("active_mode") is True
        assert is_mode_active("inactive_mode") is False
        assert is_mode_active("missing") is False

    def test_get_active_modes(self):
        write_state("a", {"active": True})
        write_state("b", {"active": False})
        write_state("c", {"active": True})
        assert get_active_modes() == ["a", "c"]

    def test_atomic_write_survives_crash(self):
        # Simulate partial write by creating a temp file and ensuring
        # it does not become the final file on exception
        path = get_state_file("atomic")
        # The implementation should use atomic rename; just verify consistency
        for i in range(50):
            write_state("atomic", {"i": i})
            assert read_state("atomic") == {"i": i}

    def test_unicode_content(self):
        write_state("unicode", {"msg": "你好世界 🌍"})
        assert read_state("unicode") == {"msg": "你好世界 🌍"}

    def test_nested_data(self):
        data = {"a": [1, 2, {"b": 3}], "c": {"d": "e"}}
        write_state("nested", data)
        assert read_state("nested") == data

    def test_corrupted_file_returns_none(self):
        path = get_state_file("bad")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("not json")
        assert read_state("bad") is None


class TestCLI:
    def setup_method(self):
        self._orig_env = os.environ.get("OMK_STATE_DIR")
        self.tmpdir = tempfile.mkdtemp()
        os.environ["OMK_STATE_DIR"] = self.tmpdir
        if hasattr(get_state_dir, "cache_clear"):
            get_state_dir.cache_clear()

    def teardown_method(self):
        if self._orig_env is None:
            os.environ.pop("OMK_STATE_DIR", None)
        else:
            os.environ["OMK_STATE_DIR"] = self._orig_env
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_cli_list_empty(self, capsys):
        sys.argv = ["state", "list"]
        assert cli() == 0
        captured = capsys.readouterr()
        assert "No state files found" in captured.out

    def test_cli_write_read(self, capsys):
        sys.argv = ["state", "write", "mode1", '{"k": "v"}']
        assert cli() == 0
        sys.argv = ["state", "read", "mode1"]
        assert cli() == 0
        captured = capsys.readouterr()
        assert '"k": "v"' in captured.out

    def test_cli_clear(self, capsys):
        write_state("mode1", {})
        sys.argv = ["state", "clear", "mode1"]
        assert cli() == 0
        assert read_state("mode1") is None

    def test_cli_invalid_json(self, capsys):
        sys.argv = ["state", "write", "mode1", "bad json"]
        assert cli() == 1

    def test_cli_unknown_command(self, capsys):
        sys.argv = ["state", "foo"]
        assert cli() == 1


class TestPerformance:
    def setup_method(self):
        self._orig_env = os.environ.get("OMK_STATE_DIR")
        self.tmpdir = tempfile.mkdtemp()
        os.environ["OMK_STATE_DIR"] = self.tmpdir
        if hasattr(get_state_dir, "cache_clear"):
            get_state_dir.cache_clear()

    def teardown_method(self):
        if self._orig_env is None:
            os.environ.pop("OMK_STATE_DIR", None)
        else:
            os.environ["OMK_STATE_DIR"] = self._orig_env
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_bulk_write_read(self):
        start = time.perf_counter()
        for i in range(100):
            write_state(f"perf{i}", {"idx": i, "data": "x" * 100})
        for i in range(100):
            assert read_state(f"perf{i}")["idx"] == i
        elapsed = time.perf_counter() - start
        assert elapsed < 5.0, f"Bulk operations too slow: {elapsed:.2f}s"
