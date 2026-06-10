"""插件注册协议。"""

from __future__ import annotations
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    import click


@runtime_checkable
class PluginProtocol(Protocol):
    """bykpy 插件协议。

    就两个成员：
        commands:  {子命令名: 描述}，用于仪表盘展示
        register:  实例方法，接收 cli，在此添加子命令
    """

    commands: dict[str, str]

    def register(self, cli: "click.Group") -> None: ...
