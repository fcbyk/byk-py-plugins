"""运行环境信息。"""

from __future__ import annotations

from dataclasses import dataclass
import platform
import sys


@dataclass(slots=True)
class EnvironmentInfo:
    """CLI 运行环境信息。"""

    app_name: str
    version: str
    python_version: str
    executable: str
    platform_name: str


def collect_environment(app_name: str, version: str) -> EnvironmentInfo:
    """收集当前运行环境。"""
    return EnvironmentInfo(
        app_name=app_name,
        version=version,
        python_version=platform.python_version(),
        executable=sys.executable,
        platform_name=platform.platform(),
    )
