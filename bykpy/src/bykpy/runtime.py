"""运行时装配。"""

from __future__ import annotations

import logging

from bykpy import __version__
from bykpy.core.context import AppContext
from bykpy.core.environment import collect_environment
from bykpy.infra.logging import create_command_logger, setup_logging
from bykpy.infra.persistence import build_path_layout
from bykpy.infra.state import JsonStateStore


class _RuntimeAppContext(AppContext):
    """运行时上下文，带缓存。"""

    _store_cache: dict[str, JsonStateStore]
    _command_store_cache: dict[tuple[str, str], JsonStateStore]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._store_cache = {}
        self._command_store_cache = {}

    def command_store(self, command_name: str, name: str = "state"):
        key = (command_name, name)
        if key not in self._command_store_cache:
            self._command_store_cache[key] = JsonStateStore(
                path=self.paths.command_state_file(command_name, f"{name}.json"),
            )
        return self._command_store_cache[key]

    def store(self, name: str = "byk.config"):
        if name not in self._store_cache:
            self._store_cache[name] = JsonStateStore(
                path=self.paths.state_file(name),
            )
        return self._store_cache[name]

    def get_command_logger(self, command_name: str) -> logging.Logger:
        return create_command_logger(self, command_name)


def build_runtime() -> AppContext:
    """构建应用运行时。"""
    app_name = "byk"
    paths = build_path_layout(app_name=app_name)
    environment = collect_environment(app_name=app_name, version=__version__)
    global_logger = setup_logging(paths.app_log_file)

    return _RuntimeAppContext(
        app_name=app_name,
        version=__version__,
        paths=paths,
        environment=environment,
        logger=global_logger,
    )
