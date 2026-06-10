"""Web 应用辅助工具。

本模块依赖 flask —— 调用任何函数前请确保已安装，否则抛出清晰错误。
在你的 pyproject.toml 中声明 flask 依赖即可：

    dependencies = [
        "flask>=2.0",
        ...
    ]
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

# ── werkzeug 日志默认太吵，模块加载时静音 ──────────────────────────
log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)


# ── dependency guard ────────────────────────────────────────────────

def _require_flask() -> None:
    """校验 flask 是否可用，不可用则抛出带安装指引的错误。"""
    try:
        import flask  # noqa: F401
    except ImportError:
        raise ImportError(
            "flask is required for bykpy.api.web.\n"
            "Install it and add to your plugin dependencies:\n"
            "    pip install flask\n"
            "    # then add 'flask>=2.0' to pyproject.toml dependencies"
        )


# ── SPA 应用工厂 ────────────────────────────────────────────────────

def create_spa(
    static_dir: str | Path,
    entry_html: str = "index.html",
    page: list[str] | None = None,
    cli_data: Any = None,
):
    """创建托管单页应用 (SPA) 的 Flask 实例。

    自动映射 /assets/* 到静态资源目录，并将所有未知路由回退到
    entry_html（支持前端路由）。响应添加无缓存头。

    Args:
        static_dir: 打包后的 SPA 根目录（含 index.html 和 assets/）。
        entry_html: SPA 入口文件名，默认 index.html。
        page: 多页面路由列表，如 ["/admin", "/login"]。
        cli_data: 可选，挂载到 app.cli_data 供后续使用。

    Returns:
        Flask 应用实例。
    """
    _require_flask()
    from flask import Flask, make_response, send_from_directory

    static_dir = Path(static_dir).resolve()
    assets_dir = static_dir / "assets"

    app = Flask(
        __name__,
        static_folder=str(assets_dir),
        static_url_path="/assets",
    )

    # ---- 单页面路由 ----
    @app.route("/")
    def index():
        response = make_response(
            send_from_directory(str(static_dir), entry_html)
        )
        response.headers["Cache-Control"] = (
            "no-cache, no-store, must-revalidate"
        )
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

    # ---- 多页面路由 ----
    if page:
        for url in page:

            def view(
                _entry_html: str = entry_html,
                _static_dir: str = str(static_dir),
            ):
                response = make_response(
                    send_from_directory(_static_dir, _entry_html)
                )
                response.headers["Cache-Control"] = (
                    "no-cache, no-store, must-revalidate"
                )
                response.headers["Pragma"] = "no-cache"
                response.headers["Expires"] = "0"
                return response

            endpoint = f"page_{url.strip('/').replace('/', '_') or 'root'}"
            app.add_url_rule(url, endpoint, view)

    # ---- 附加数据 ----
    if cli_data is not None:
        app.cli_data = cli_data

    return app


# ── API 统一响应 ────────────────────────────────────────────────────

class R:
    """Web API 统一响应格式。"""

    @staticmethod
    def success(
        data: Any = None,
        message: str = "success",
    ):
        """构造成功响应。

        Returns:
            (Flask Response, 200)
        """
        _require_flask()
        from flask import jsonify

        return jsonify({
            "code": 200,
            "message": message,
            "data": data,
        }), 200

    @staticmethod
    def error(
        message: str = "error",
        code: int = 400,
        data: Any = None,
    ):
        """构造错误响应。

        Returns:
            (Flask Response, <code>)
        """
        _require_flask()
        from flask import jsonify

        return jsonify({
            "code": code,
            "message": message,
            "data": data,
        }), code


# ── 请求工具 ────────────────────────────────────────────────────────

def get_client_ip() -> str:
    """从当前 Flask 请求上下文中提取客户端 IP。

    优先使用 X-Forwarded-For 头（取第一个），
    回退到 request.remote_addr。

    Returns:
        客户端 IP 字符串，无法获取时返回 "unknown"。
    """
    _require_flask()
    from flask import request

    xff = request.headers.get("X-Forwarded-For", "")
    if xff:
        return xff.split(",")[0].strip()
    return request.remote_addr or "unknown"
