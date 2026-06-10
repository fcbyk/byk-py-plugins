"""状态存储的 JSON 文件实现。"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from bykpy.core.state import StateStore
from bykpy.infra.persistence import read_json, write_json


@dataclass(slots=True)
class JsonStateStore:
    """基于 JSON 文件的状态存储实现。"""

    path: Path

    def load(self) -> dict[str, Any]:
        """读取完整状态。"""
        data = read_json(self.path, default={})
        return data if isinstance(data, dict) else {}

    def save(self, data: dict[str, Any]) -> dict[str, Any]:
        """覆盖保存完整状态。"""
        write_json(self.path, data)
        return data

    def get(self, key: str, default: Any = None) -> Any:
        """读取单个状态值。"""
        return self.load().get(key, default)

    def set(self, key: str, value: Any) -> dict[str, Any]:
        """保存单个状态值。"""
        data = self.load()
        data[key] = value
        return self.save(data)

    def update(self, values: dict[str, Any]) -> dict[str, Any]:
        """批量更新状态。"""
        data = self.load()
        data.update(values)
        return self.save(data)

    def delete(self, key: str) -> dict[str, Any]:
        """删除单个状态值。"""
        data = self.load()
        data.pop(key, None)
        return self.save(data)

    def clear(self) -> dict[str, Any]:
        """清空当前状态文件。"""
        return self.save({})
