"""统一持久化路径与基础文件操作。"""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
from typing import Any, TypeVar

from bykpy.core.errors import CliError
from bykpy.core.persistence import PathLayout

T = TypeVar("T")

def build_path_layout(app_name: str) -> PathLayout:
    """构建目录布局并确保目录存在。"""
    root_dir = Path.home() / f".{app_name}"
    state_dir = root_dir / "state"
    logs_dir = root_dir / "logs"
    runtime_dir = root_dir / "runtime"
    cache_dir = root_dir / "cache"

    for directory in (root_dir, state_dir, logs_dir, runtime_dir, cache_dir):
        directory.mkdir(parents=True, exist_ok=True)

    return PathLayout(
        root_dir=root_dir,
        state_dir=state_dir,
        logs_dir=logs_dir,
        runtime_dir=runtime_dir,
        app_log_file=logs_dir / "app.log",
        cache_dir=cache_dir,
    )


def read_json(path: Path, default: T) -> T:
    """读取 JSON 文件。"""
    if not path.exists():
        return default

    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as exc:
        raise CliError(f"Failed to parse JSON file: {path}") from exc
    except OSError as exc:
        raise CliError(f"Unable to read file: {path}") from exc

    return data if data is not None else default


def write_json(path: Path, data: Any) -> None:
    """以原子方式写入 JSON 文件。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            delete=False,
            dir=path.parent,
            encoding="utf-8",
        ) as temp_file:
            json.dump(data, temp_file, indent=2, ensure_ascii=False)
            temp_path = Path(temp_file.name)
        temp_path.replace(path)
    except OSError as exc:
        raise CliError(f"Unable to write file: {path}") from exc


def read_text(path: Path, default: str | None = None) -> str | None:
    """读取文本文件。"""
    if not path.exists():
        return default
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise CliError(f"Unable to read file: {path}") from exc


def write_text(path: Path, content: str) -> None:
    """以原子方式写入文本文件。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            delete=False,
            dir=path.parent,
            encoding="utf-8",
        ) as temp_file:
            temp_file.write(content)
            temp_path = Path(temp_file.name)
        temp_path.replace(path)
    except OSError as exc:
        raise CliError(f"Unable to write file: {path}") from exc
