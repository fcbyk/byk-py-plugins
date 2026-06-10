"""统一异常定义。"""

from __future__ import annotations


class CliError(RuntimeError):
    """面向终端用户的业务异常。"""
