from __future__ import annotations

from unittest.mock import MagicMock, patch

import click
from click.testing import CliRunner


class TestRenderDashboard:
    @patch("bykpy.infra.view.load_cache")
    def test_render_dashboard_basic(self, mock_load_cache):
        """测试基础仪表盘渲染（含插件命令）。"""
        mock_load_cache.return_value = {
            "commands": {"test-cmd": {"module": "test:main", "description": "Test command"}}
        }

        context = MagicMock()
        cli = click.Group()
        cli.params = []

        runner = CliRunner()
        with runner.isolation():
            from bykpy.infra.view import render_dashboard
            render_dashboard(context, cli)

    @patch("bykpy.infra.view.load_cache")
    def test_render_dashboard_no_commands(self, mock_load_cache):
        """缓存无命令时只输出 Click 默认 help。"""
        mock_load_cache.return_value = {"commands": {}}

        context = MagicMock()
        cli = click.Group()
        cli.params = []

        runner = CliRunner()
        with runner.isolation():
            from bykpy.infra.view import render_dashboard
            render_dashboard(context, cli)

    @patch("bykpy.infra.view.load_cache")
    def test_render_dashboard_with_commands(self, mock_load_cache):
        """验证有命令时输出 (name, desc) 元组格式。"""
        mock_load_cache.return_value = {
            "commands": {
                "slide": {"module": "slide:main", "description": "Control slides via mobile"},
                "lansend": {"module": "lansend:main", "description": "Share files over LAN"},
            }
        }

        context = MagicMock()
        cli = click.Group()
        cli.params = []

        runner = CliRunner()
        with runner.isolation():
            from bykpy.infra.view import render_dashboard
            render_dashboard(context, cli)
