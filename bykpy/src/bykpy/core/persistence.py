"""持久化路径布局。"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class PathLayout:
    """持久化目录布局数据结构。"""

    root_dir: Path
    state_dir: Path
    logs_dir: Path
    runtime_dir: Path
    app_log_file: Path
    cache_dir: Path

    @staticmethod
    def _validate_safe_name(value: str, field_name: str) -> str:
        """校验名称安全性，防止路径穿越和脏数据文件名。"""
        normalized = value.strip()
        if not normalized:
            raise ValueError(f"{field_name} 不能为空")
        if normalized in {".", ".."}:
            raise ValueError(f"{field_name} 不能为 '.' 或 '..'")
        if "/" in normalized or "\\" in normalized:
            raise ValueError(f"{field_name} 不能包含路径分隔符")
        return normalized

    def command_state_dir(self, command_name: str) -> Path:
        """返回子命令专属目录。"""
        safe_command_name = self._validate_safe_name(command_name, "command_name")
        path = self.state_dir / safe_command_name
        path.mkdir(parents=True, exist_ok=True)
        return path

    def command_state_file(self, command_name: str, *parts: str) -> Path:
        """返回子命令专属文件路径。"""
        target = self.command_state_dir(command_name)
        for part in parts:
            safe_part = self._validate_safe_name(part, "part")
            target = target / safe_part
        target.parent.mkdir(parents=True, exist_ok=True)
        return target

    def state_file(self, name: str) -> Path:
        """返回应用级状态文件路径。"""
        safe_name = self._validate_safe_name(name, "name")
        path = self.state_dir / f"{safe_name}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        return path
