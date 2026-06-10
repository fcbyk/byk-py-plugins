"""面向子命令的上下文封装。"""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import update_wrapper
import logging
from typing import Any, Callable, TypeVar, cast

import click

from bykpy.app import CliState
from bykpy.core.context import AppContext, CommandContextLike
from bykpy.core.state import StateStore

F = TypeVar("F", bound=Callable[..., Any])


@dataclass(slots=True)
class CommandContext(CommandContextLike):
    """提供给子命令的便捷上下文。"""

    name: str
    app: AppContext
    logger: logging.Logger
    _state_cache: dict[str, StateStore] = field(default_factory=dict, init=False, repr=False)

    def state(self, name: str = "state") -> StateStore:
        """获取当前命令的专属存储。"""
        if name not in self._state_cache:
            self._state_cache[name] = self.app.command_store(self.name, name)
        return self._state_cache[name]

def _get_group_name(ctx: click.Context) -> str:
    """获取二级命令名"""
    node = ctx
    while node.parent and node.parent.parent is not None:
        node = node.parent
    return node.command.name or "unknown"

def build_command_context(ctx: click.Context) -> CommandContext:
    """根据当前 Click 上下文构建命令上下文"""
    state = cast(CliState, ctx.obj)
    command_name = _get_group_name(ctx)
    return CommandContext(
        name=command_name,
        app=state.context,
        logger=state.context.get_command_logger(command_name),
    )


def pass_command_context(func: F) -> F:
    """向子命令注入便捷上下文。"""

    @click.pass_context
    def new_func(ctx: click.Context, *args: Any, **kwargs: Any) -> Any:
        return ctx.invoke(func, build_command_context(ctx), *args, **kwargs)

    return cast(F, update_wrapper(new_func, func))


def get_app_context() -> AppContext:
    """获取当前应用上下文。"""
    from bykpy.runtime import build_runtime
    return build_runtime()
