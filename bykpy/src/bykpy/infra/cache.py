"""插件缓存：entry_points 元数据扫描与磁盘缓存。

启动时只需一次 IO 读 app.json，plugins 数量不影响启动性能。
pip install/uninstall 后 site-packages mtime 变化自动触发缓存重建。
"""

from __future__ import annotations

import importlib
import logging
import os
import site
import time
from importlib.metadata import entry_points
from pathlib import Path

from bykpy.infra.persistence import read_json, write_json

logger = logging.getLogger("bykpy")


def get_watched_mtimes() -> dict[str, float]:
    """收集 site-packages 目录的 mtime，用于缓存失效检测。"""
    mtimes: dict[str, float] = {}
    try:
        paths = site.getsitepackages()
    except Exception:
        return mtimes
    for p in paths:
        if os.path.exists(p):
            try:
                mtimes[p] = os.path.getmtime(p)
            except OSError:
                pass
    return mtimes


def is_cache_stale(cached_mtimes: dict[str, float]) -> bool:
    """对比当前 mtime 与缓存，判断缓存是否失效。"""
    current = get_watched_mtimes()
    return current != cached_mtimes


def scan_plugins() -> dict[str, dict[str, str]]:
    """扫描 entry_points，import 插件类展开 commands。

    对每个 entry_point，import 其 Plugin 类，读取 commands dict，
    展开为扁平 {命令名: {module, description}} 结构。
    """
    commands: dict[str, dict[str, str]] = {}

    try:
        plugin_entries = entry_points(group="bykpy.plugins")
    except TypeError:
        plugin_entries = entry_points().get("bykpy.plugins", [])  # type: ignore[attr-defined]

    for ep in plugin_entries:
        try:
            module_name, class_name = ep.value.rsplit(":", 1)
            module = importlib.import_module(module_name)
            plugin_cls = getattr(module, class_name)
            for cmd, desc in plugin_cls.commands.items():
                if cmd in commands:
                    logger.warning(
                        "command '%s' from %s overrides existing from %s",
                        cmd, ep.value, commands[cmd]["module"],
                    )
                commands[cmd] = {
                    "module": ep.value,
                    "description": desc,
                }
        except Exception as e:
            logger.warning(
                "插件 %s 加载失败，可能不兼容当前 bykpy 版本: %s", ep.name, e
            )

    return commands


def _build_cache() -> dict:
    """构建缓存数据结构。"""
    import sys
    return {
        "watched_mtimes": get_watched_mtimes(),
        "scanned_at": time.time(),
        "python_executable": sys.executable,
        "commands": scan_plugins(),
    }


def load_cache(cache_file: Path) -> dict:
    """读取缓存文件，失效时自动重建。

    Args:
        cache_file: ~/.byk/cache/app.json 路径

    Returns:
        缓存数据 dict，保证 commands 键存在
    """
    data = read_json(cache_file, default=None)

    if data is None:
        data = _build_cache()
        write_json(cache_file, data)
        return data

    cached_mtimes = data.get("watched_mtimes", {})
    if is_cache_stale(cached_mtimes):
        data = _build_cache()
        write_json(cache_file, data)
        return data

    return data
