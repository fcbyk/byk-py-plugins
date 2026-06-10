from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from bykpy.core.errors import CliError
from bykpy.infra.persistence import (
    build_path_layout,
    read_json,
    read_text,
    write_json,
    write_text,
)


class TestBuildPathLayout:
    def test_creates_directories(self, tmp_path, monkeypatch):
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        layout = build_path_layout("testapp")

        assert (tmp_path / ".testapp").exists()
        assert (tmp_path / ".testapp" / "state").exists()
        assert (tmp_path / ".testapp" / "logs").exists()
        assert (tmp_path / ".testapp" / "runtime").exists()
        assert (tmp_path / ".testapp" / "cache").exists()

    def test_returns_correct_paths(self, tmp_path, monkeypatch):
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        layout = build_path_layout("testapp")

        assert layout.root_dir == tmp_path / ".testapp"
        assert layout.state_dir == tmp_path / ".testapp" / "state"
        assert layout.logs_dir == tmp_path / ".testapp" / "logs"
        assert layout.runtime_dir == tmp_path / ".testapp" / "runtime"
        assert layout.cache_dir == tmp_path / ".testapp" / "cache"
        assert layout.app_log_file == tmp_path / ".testapp" / "logs" / "app.log"


class TestReadJson:
    def test_read_existing_file(self, tmp_path):
        path = tmp_path / "test.json"
        data = {"key": "value", "number": 42}
        path.write_text(json.dumps(data))

        result = read_json(path, default={})
        assert result == data

    def test_return_default_if_not_exists(self, tmp_path):
        path = tmp_path / "nonexistent.json"
        result = read_json(path, default={"default": "value"})
        assert result == {"default": "value"}

    def test_return_default_if_null(self, tmp_path):
        path = tmp_path / "test.json"
        path.write_text("null")

        result = read_json(path, default={"default": "value"})
        assert result == {"default": "value"}

    def test_raises_on_invalid_json(self, tmp_path):
        path = tmp_path / "test.json"
        path.write_text("not valid json")

        with pytest.raises(CliError) as exc_info:
            read_json(path, default={})
        assert "Failed to parse JSON" in str(exc_info.value)

    def test_raises_on_os_error(self, tmp_path):
        path = tmp_path / "test.json"
        path.write_text('{"key": "value"}')

        with patch("pathlib.Path.open") as mock_open:
            mock_open.side_effect = OSError("Permission denied")
            with pytest.raises(CliError) as exc_info:
                read_json(path, default={})
            assert "Unable to read file" in str(exc_info.value)


class TestWriteJson:
    def test_write_json_file(self, tmp_path):
        path = tmp_path / "test.json"
        data = {"key": "value", "number": 42}

        write_json(path, data)

        result = json.loads(path.read_text())
        assert result == data

    def test_creates_parent_directories(self, tmp_path):
        path = tmp_path / "subdir" / "test.json"
        data = {"key": "value"}

        write_json(path, data)

        assert path.exists()

    def test_atomic_write(self, tmp_path):
        path = tmp_path / "test.json"
        data = {"key": "value"}

        write_json(path, data)

        temp_files = list(tmp_path.glob("*.tmp"))
        assert len(temp_files) == 0

    def test_raises_on_os_error(self, tmp_path):
        path = tmp_path / "test.json"

        with patch("tempfile.NamedTemporaryFile") as mock_temp:
            mock_temp.side_effect = OSError("Permission denied")
            with pytest.raises(CliError) as exc_info:
                write_json(path, {"key": "value"})
            assert "Unable to write file" in str(exc_info.value)


class TestReadText:
    def test_read_existing_file(self, tmp_path):
        path = tmp_path / "test.txt"
        content = "Hello, World!"
        path.write_text(content)

        result = read_text(path)
        assert result == content

    def test_return_default_if_not_exists(self, tmp_path):
        path = tmp_path / "nonexistent.txt"
        result = read_text(path, default="default content")
        assert result == "default content"

    def test_return_none_if_not_exists_no_default(self, tmp_path):
        path = tmp_path / "nonexistent.txt"
        result = read_text(path)
        assert result is None

    def test_raises_on_os_error(self, tmp_path):
        path = tmp_path / "test.txt"
        path.write_text("content")

        with patch("pathlib.Path.read_text") as mock_read:
            mock_read.side_effect = OSError("Permission denied")
            with pytest.raises(CliError) as exc_info:
                read_text(path)
            assert "Unable to read file" in str(exc_info.value)


class TestWriteText:
    def test_write_text_file(self, tmp_path):
        path = tmp_path / "test.txt"
        content = "Hello, World!"

        write_text(path, content)

        result = path.read_text()
        assert result == content

    def test_creates_parent_directories(self, tmp_path):
        path = tmp_path / "subdir" / "test.txt"
        content = "Hello!"

        write_text(path, content)

        assert path.exists()

    def test_atomic_write(self, tmp_path):
        path = tmp_path / "test.txt"
        content = "Hello!"

        write_text(path, content)

        temp_files = list(tmp_path.glob("*.tmp"))
        assert len(temp_files) == 0

    def test_raises_on_os_error(self, tmp_path):
        path = tmp_path / "test.txt"

        with patch("tempfile.NamedTemporaryFile") as mock_temp:
            mock_temp.side_effect = OSError("Permission denied")
            with pytest.raises(CliError) as exc_info:
                write_text(path, "content")
            assert "Unable to write file" in str(exc_info.value)
