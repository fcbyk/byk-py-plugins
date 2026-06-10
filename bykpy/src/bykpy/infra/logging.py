"""统一日志初始化。"""

from __future__ import annotations

import logging
from pathlib import Path

from bykpy.core.context import AppContext


def _get_log_config(context: AppContext) -> dict:
    """从配置文件读取日志配置。"""
    try:
        logging_config = context.store("byk.config").get("logging", {})
        if isinstance(logging_config, dict):
            return logging_config
    except Exception:
        pass
    return {}


def setup_logging(app_log_file: Path) -> logging.Logger:
    """初始化应用日志。"""
    logger = logging.getLogger("bykpy")
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(app_log_file, encoding="utf-8")
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s %(levelname)s [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    logger.addHandler(handler)
    logger.propagate = False
    logger.debug("logger initialized")
    return logger


def create_command_logger(context: AppContext, command_name: str) -> logging.Logger:
    """创建命令专属 logger"""
    logger = logging.getLogger(f"bykpy.{command_name}")

    if not logger.handlers:
        log_config = _get_log_config(context)
        level_str = log_config.get("level", "INFO").upper()
        separate = log_config.get("separate", True)

        try:
            level = getattr(logging, level_str)
        except AttributeError:
            level = logging.INFO

        logger.setLevel(level)

        log_file = context.paths.logs_dir / f"{command_name}.log"
        handler = logging.FileHandler(log_file, encoding="utf-8")
        handler.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s %(levelname)s [%(name)s] %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        logger.addHandler(handler)

        logger.propagate = not separate

    return logger
