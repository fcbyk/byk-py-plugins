"""面向子命令和插件的公开运行时 API。"""

from bykpy.api.context import CommandContext, pass_command_context, get_app_context

from bykpy.api.network import (
    get_private_networks,
    ensure_port_available,
)

# ── CLI 工具 ────────────────────────────────────────────────────────
from bykpy.api.cli import (
    check_port,
    colored_key_value,
    copy_to_clipboard,
    echo_network_urls,
    open_browser,
    wait_for_server_ready,
)

# ── Web 工具（需要 flask） ──────────────────────────────────────────
from bykpy.api.web import (
    create_spa,
    get_client_ip,
    R,
)

from bykpy.core.state import StateStore

__all__ = [
    # 上下文
    "CommandContext",
    "pass_command_context",
    "get_app_context",
    # 网络工具
    "get_private_networks",
    "ensure_port_available",
    # CLI 工具
    "check_port",
    "colored_key_value",
    "copy_to_clipboard",
    "echo_network_urls",
    "open_browser",
    "wait_for_server_ready",
    # Web 工具
    "create_spa",
    "get_client_ip",
    "R",
    # 状态存储
    "StateStore",
]
