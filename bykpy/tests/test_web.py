"""Tests for bykpy.api.web"""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from bykpy.api.web import R, create_spa, get_client_ip


# ── create_spa ──────────────────────────────────────────────────────

class TestCreateSpa:
    def test_creates_flask_app(self):
        """基本场景：创建 Flask 应用。"""
        with tempfile.TemporaryDirectory() as tmp:
            dist_dir = Path(tmp) / "dist"
            dist_dir.mkdir()
            (dist_dir / "assets").mkdir()
            (dist_dir / "index.html").write_text("<html></html>")

            app = create_spa(str(dist_dir))

            assert app is not None
            # 验证路由 "/" 存在
            rule_strings = [str(rule) for rule in app.url_map.iter_rules()]
            assert any("/" == r for r in rule_strings)
            assert any("/assets/" in r for r in rule_strings)

    def test_index_returns_html_with_no_cache(self):
        """首页返回 HTML，带无缓存头。"""
        with tempfile.TemporaryDirectory() as tmp:
            dist_dir = Path(tmp) / "dist"
            dist_dir.mkdir()
            (dist_dir / "assets").mkdir()
            (dist_dir / "index.html").write_text(
                "<!doctype html><html><body>hello</body></html>"
            )

            app = create_spa(str(dist_dir))
            client = app.test_client()
            resp = client.get("/")

            assert resp.status_code == 200
            assert b"hello" in resp.data
            assert resp.headers["Cache-Control"] == (
                "no-cache, no-store, must-revalidate"
            )
            assert resp.headers["Pragma"] == "no-cache"
            assert resp.headers["Expires"] == "0"

    def test_multi_page_routes(self):
        """多页面路由。"""
        with tempfile.TemporaryDirectory() as tmp:
            dist_dir = Path(tmp) / "dist"
            dist_dir.mkdir()
            (dist_dir / "assets").mkdir()
            (dist_dir / "index.html").write_text("home")

            app = create_spa(str(dist_dir), page=["/admin"])
            client = app.test_client()

            resp = client.get("/admin")
            assert resp.status_code == 200
            assert b"home" in resp.data

    def test_cli_data_attached(self):
        """cli_data 挂载到 app 实例。"""
        with tempfile.TemporaryDirectory() as tmp:
            dist_dir = Path(tmp) / "dist"
            dist_dir.mkdir()
            (dist_dir / "assets").mkdir()
            (dist_dir / "index.html").write_text("")

            my_data = {"foo": "bar"}
            app = create_spa(str(dist_dir), cli_data=my_data)
            assert app.cli_data == my_data

    def test_cli_data_none_when_omitted(self):
        """不传 cli_data 时不设置该属性。"""
        with tempfile.TemporaryDirectory() as tmp:
            dist_dir = Path(tmp) / "dist"
            dist_dir.mkdir()
            (dist_dir / "assets").mkdir()
            (dist_dir / "index.html").write_text("")

            app = create_spa(str(dist_dir))
            assert not hasattr(app, "cli_data")

    def test_custom_entry_html(self):
        """自定义入口文件名。"""
        with tempfile.TemporaryDirectory() as tmp:
            dist_dir = Path(tmp) / "dist"
            dist_dir.mkdir()
            (dist_dir / "assets").mkdir()
            (dist_dir / "review.html").write_text("review page")

            app = create_spa(str(dist_dir), entry_html="review.html")
            client = app.test_client()
            resp = client.get("/")
            assert resp.status_code == 200
            assert b"review page" in resp.data

    def test_static_assets_served(self):
        """静态资源可正常访问。"""
        with tempfile.TemporaryDirectory() as tmp:
            dist_dir = Path(tmp) / "dist"
            assets_dir = dist_dir / "assets"
            assets_dir.mkdir(parents=True)
            (dist_dir / "index.html").write_text("")
            (assets_dir / "style.css").write_text("body { color: red; }")

            app = create_spa(str(dist_dir))
            client = app.test_client()
            resp = client.get("/assets/style.css")
            assert resp.status_code == 200
            assert b"color: red" in resp.data

    def test_missing_flask_raises(self):
        """flask 未安装时抛出清晰的 ImportError。"""
        with patch("bykpy.api.web._require_flask") as mock_guard:
            mock_guard.side_effect = ImportError(
                "flask is required for bykpy.api.web.\n"
                "Install it and add to your plugin dependencies:\n"
                "    pip install flask\n"
            )
            with pytest.raises(ImportError, match="flask is required"):
                create_spa("/nonexistent")


# ── R (API response helper) ─────────────────────────────────────────

class TestR:
    def test_success_default(self, app):
        """默认 success 响应。"""
        with app.test_request_context("/"):
            resp, status = R.success()
        data = resp.get_json()
        assert status == 200
        assert data["code"] == 200
        assert data["message"] == "success"
        assert data["data"] is None

    def test_success_with_data(self, app):
        with app.test_request_context("/"):
            resp, status = R.success(data={"id": 1})
        data = resp.get_json()
        assert status == 200
        assert data["data"] == {"id": 1}

    def test_success_with_message(self, app):
        with app.test_request_context("/"):
            resp, status = R.success(message="created")
        assert status == 200
        assert resp.get_json()["message"] == "created"

    def test_error_default(self, app):
        """默认 error 响应。"""
        with app.test_request_context("/"):
            resp, status = R.error()
        data = resp.get_json()
        assert status == 400
        assert data["code"] == 400
        assert data["message"] == "error"

    def test_error_custom(self, app):
        with app.test_request_context("/"):
            resp, status = R.error(message="Not Found", code=404)
        data = resp.get_json()
        assert status == 404
        assert data["code"] == 404
        assert data["message"] == "Not Found"

    def test_error_with_data(self, app):
        with app.test_request_context("/"):
            resp, status = R.error(
                message="Validation failed", code=422, data={"field": "name"}
            )
        data = resp.get_json()
        assert status == 422
        assert data["data"] == {"field": "name"}

    def test_missing_flask_raises(self):
        """flask 未安装时抛出清晰的 ImportError。"""
        with patch("bykpy.api.web._require_flask") as mock_guard:
            mock_guard.side_effect = ImportError(
                "flask is required for bykpy.api.web.\n"
                "Install it and add to your plugin dependencies:\n"
                "    pip install flask\n"
            )
            with pytest.raises(ImportError, match="flask is required"):
                R.success()

            with pytest.raises(ImportError, match="flask is required"):
                R.error()


# ── get_client_ip ───────────────────────────────────────────────────

class TestGetClientIp:
    def test_remote_addr(self, app):
        """从 remote_addr 获取 IP。"""
        with app.test_request_context("/", environ_base={"REMOTE_ADDR": "192.168.1.1"}):
            assert get_client_ip() == "192.168.1.1"

    def test_x_forwarded_for(self, app):
        """X-Forwarded-For 头优先。"""
        with app.test_request_context(
            "/",
            environ_base={"REMOTE_ADDR": "10.0.0.1"},
            headers={"X-Forwarded-For": "203.0.113.1, 10.0.0.1"},
        ):
            assert get_client_ip() == "203.0.113.1"

    def test_x_forwarded_for_single(self, app):
        """单个 X-Forwarded-For 值。"""
        with app.test_request_context(
            "/",
            headers={"X-Forwarded-For": "203.0.113.1"},
        ):
            assert get_client_ip() == "203.0.113.1"

    def test_no_remote_addr(self, app):
        """没有 remote_addr 时返回 "unknown"。"""
        with app.test_request_context("/", environ_base={"REMOTE_ADDR": ""}):
            assert get_client_ip() == "unknown"

    def test_empty_x_forwarded_for(self, app):
        """X-Forwarded-For 为空字符串时回退到 remote_addr。"""
        with app.test_request_context(
            "/",
            environ_base={"REMOTE_ADDR": "10.0.0.1"},
            headers={"X-Forwarded-For": ""},
        ):
            assert get_client_ip() == "10.0.0.1"

    def test_missing_flask_raises(self):
        """flask 未安装时抛出清晰的 ImportError。"""
        with patch("bykpy.api.web._require_flask") as mock_guard:
            mock_guard.side_effect = ImportError(
                "flask is required for bykpy.api.web.\n"
                "Install it and add to your plugin dependencies:\n"
                "    pip install flask\n"
            )
            with pytest.raises(ImportError, match="flask is required"):
                get_client_ip()
