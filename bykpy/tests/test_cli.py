from __future__ import annotations

from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from bykpy.app import create_cli


def build_cli():
    return create_cli()


def test_dashboard_no_commands_without_plugins(tmp_path, monkeypatch):
    """无插件时仪表盘不显示 Commands 段。"""
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.chdir(tmp_path)

    with patch("bykpy.infra.cache.entry_points", MagicMock(return_value=[])):
        runner = CliRunner()
        result = runner.invoke(build_cli(), [])

    assert result.exit_code == 0
    assert "Commands:" not in result.output


def test_version_option(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))

    runner = CliRunner()
    result = runner.invoke(build_cli(), ["--version"])

    assert result.exit_code == 0
    assert result.output.strip().startswith("v")
