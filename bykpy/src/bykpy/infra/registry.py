"""插件发现与注册。"""

from __future__ import annotations

import importlib
import logging

import click

logger = logging.getLogger("bykpy")


def load_single_plugin(cli: click.Group, cmd_name: str, module_path: str) -> None:
    """按需加载单个插件：import → 实例化 → plugin.register(cli)。

    Args:
        cli: Click Group 对象
        cmd_name: 命令名（用于日志）
        module_path: "hello.byk:Plugin" 格式的导入路径（包.模块:类名）
    """
    module_name, class_name = module_path.rsplit(":", 1)
    module = importlib.import_module(module_name)
    plugin_cls = getattr(module, class_name)
    plugin = plugin_cls()
    plugin.register(cli)
    logger.debug("plugin loaded on demand: %s from %s", cmd_name, module_path)
