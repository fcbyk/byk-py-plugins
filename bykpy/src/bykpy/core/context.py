"""CLI 运行时上下文。"""

from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import TYPE_CHECKING, Protocol

from bykpy.core.environment import EnvironmentInfo
from bykpy.core.persistence import PathLayout

if TYPE_CHECKING:
    from bykpy.core.state import StateStore


class CommandContextLike(Protocol):
    """命令上下文协议。"""

    name: str
    app: "AppContext"
    logger: logging.Logger

    def state(self, name: str = "state") -> "StateStore": ...


@dataclass(slots=True)
class AppContext:
    """子命令共享的核心上下文。"""

    app_name: str
    version: str
    paths: PathLayout
    environment: EnvironmentInfo
    logger: logging.Logger

    def command_store(
        self,
        command_name: str,
        name: str = "state",
    ) -> StateStore:
        """返回某个子命令的状态存储。"""
        raise NotImplementedError

    def store(self, name: str = "byk.config") -> StateStore:
        """返回应用级共享状态存储。"""
        raise NotImplementedError

    def get_command_logger(self, command_name: str) -> logging.Logger:
        """获取命令专属 logger。"""
        raise NotImplementedError
