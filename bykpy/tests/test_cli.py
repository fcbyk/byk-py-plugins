"""Tests for bykpy.api.cli"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from bykpy.api.cli import (
    check_port,
    colored_key_value,
    copy_to_clipboard,
    echo_network_urls,
    open_browser,
    wait_for_server_ready,
)


# ── check_port ──────────────────────────────────────────────────────

class TestCheckPort:
    def test_port_available(self):
        """端口可用时返回 True，无错误输出。"""
        with patch("bykpy.api.cli.ensure_port_available") as mock_ensure:
            assert check_port(8080) is True
            mock_ensure.assert_called_once_with(port=8080, host="0.0.0.0")

    def test_port_available_custom_host(self):
        """自定义 host。"""
        with patch("bykpy.api.cli.ensure_port_available") as mock_ensure:
            assert check_port(8080, host="127.0.0.1") is True
            mock_ensure.assert_called_once_with(port=8080, host="127.0.0.1")

    def test_port_unavailable(self):
        """端口不可用时打印错误，返回 False。"""
        with patch("bykpy.api.cli.ensure_port_available") as mock_ensure:
            mock_ensure.side_effect = OSError("Address already in use")
            with patch("bykpy.api.cli.click.echo") as mock_echo:
                assert check_port(8080) is False
                assert mock_echo.call_count >= 2

    def test_port_unavailable_silent(self):
        """silent=True 时仅返回 False，不打印任何内容。"""
        with patch("bykpy.api.cli.ensure_port_available") as mock_ensure:
            mock_ensure.side_effect = OSError("Address already in use")
            with patch("bykpy.api.cli.click.echo") as mock_echo:
                assert check_port(8080, silent=True) is False
                mock_echo.assert_not_called()


# ── colored_key_value ───────────────────────────────────────────────

class TestColoredKeyValue:
    def test_basic(self):
        result = colored_key_value("key", "value")
        assert "key" in result
        assert "value" in result
        assert ": " in result

    def test_none_colors(self):
        """key_color 和 value_color 为 None 时不应报错。"""
        result = colored_key_value("key", "value", key_color=None, value_color=None)
        assert "key" in result
        assert "value" in result

    def test_non_string_value(self):
        """value 为非字符串时自动转换。"""
        result = colored_key_value("port", 8080)
        assert "8080" in result


# ── echo_network_urls ───────────────────────────────────────────────

class TestEchoNetworkUrls:
    def test_basic_output(self):
        """验证输出了本地地址。"""
        networks = [
            {
                "iface": "en0",
                "ips": ["192.168.1.100"],
                "type": "ethernet",
                "virtual": False,
            }
        ]
        with patch("bykpy.api.cli.click.echo") as mock_echo:
            echo_network_urls(networks, 8080)
            # 至少输出 localhost 和局域网地址
            assert mock_echo.call_count >= 3
            # 检查 localhost
            calls_text = " ".join(
                str(call) for call in mock_echo.call_args_list
            )
            assert "localhost:8080" in calls_text
            assert "192.168.1.100:8080" in calls_text

    def test_exclude_virtual_by_default(self):
        """默认不输出虚拟网卡地址。"""
        networks = [
            {
                "iface": "docker0",
                "ips": ["172.17.0.1"],
                "type": "container",
                "virtual": True,
            }
        ]
        with patch("bykpy.api.cli.click.echo") as mock_echo:
            echo_network_urls(networks, 8080)
            calls_text = " ".join(
                str(call) for call in mock_echo.call_args_list
            )
            assert "172.17.0.1:8080" not in calls_text

    def test_include_virtual(self):
        """include_virtual=True 时输出虚拟网卡地址。"""
        networks = [
            {
                "iface": "docker0",
                "ips": ["172.17.0.1"],
                "type": "container",
                "virtual": True,
            }
        ]
        with patch("bykpy.api.cli.click.echo") as mock_echo:
            echo_network_urls(networks, 8080, include_virtual=True)
            calls_text = " ".join(
                str(call) for call in mock_echo.call_args_list
            )
            assert "172.17.0.1:8080" in calls_text

    def test_skip_loopback_in_networks(self):
        """网络列表中的 127.0.0.1 不应重复输出。"""
        networks = [
            {
                "iface": "lo0",
                "ips": ["127.0.0.1", "192.168.1.1"],
                "type": "loopback",
                "virtual": True,
            }
        ]
        with patch("bykpy.api.cli.click.echo") as mock_echo:
            echo_network_urls(networks, 8080, include_virtual=True)
            calls_text = " ".join(
                str(call) for call in mock_echo.call_args_list
            )
            # 本地回环地址应该出现（由顶部的 localhost/127.0.0.1 产生）
            # 但网络列表中的 127.0.0.1 不应重复
            assert calls_text.count("127.0.0.1:8080") <= 1  # 仅 localhost 部分输出一次

    def test_empty_networks(self):
        """空网络列表至少输出本地地址。"""
        with patch("bykpy.api.cli.click.echo") as mock_echo:
            echo_network_urls([], 8080)
            calls_text = " ".join(
                str(call) for call in mock_echo.call_args_list
            )
            assert "localhost:8080" in calls_text
            assert "127.0.0.1:8080" in calls_text


# ── copy_to_clipboard ───────────────────────────────────────────────

class TestCopyToClipboard:
    def test_success(self):
        """成功复制时打印确认消息。"""
        with patch("pyperclip.copy") as mock_copy:
            with patch("bykpy.api.cli.click.echo") as mock_echo:
                copy_to_clipboard("http://localhost:8080")
                mock_copy.assert_called_once_with("http://localhost:8080")
                # 应输出成功消息
                assert any(
                    "copied to clipboard" in str(call)
                    for call in mock_echo.call_args_list
                )

    def test_silent(self):
        """silent=True 时不输出任何消息。"""
        with patch("pyperclip.copy") as mock_copy:
            with patch("bykpy.api.cli.click.echo") as mock_echo:
                copy_to_clipboard("http://localhost:8080", silent=True)
                mock_copy.assert_called_once()
                mock_echo.assert_not_called()

    def test_copy_exception(self):
        """pyperclip.copy 抛出异常时输出警告。"""
        with patch("pyperclip.copy") as mock_copy:
            mock_copy.side_effect = Exception("clipboard error")
            with patch("bykpy.api.cli.click.echo") as mock_echo:
                copy_to_clipboard("http://localhost:8080")
                assert any(
                    "Could not copy" in str(call)
                    for call in mock_echo.call_args_list
                )

    def test_copy_exception_silent(self):
        """silent + 异常时静默。"""
        with patch("pyperclip.copy") as mock_copy:
            mock_copy.side_effect = Exception("clipboard error")
            with patch("bykpy.api.cli.click.echo") as mock_echo:
                copy_to_clipboard("http://localhost:8080", silent=True)
                mock_echo.assert_not_called()

    def test_custom_label(self):
        """自定义 label 出现在输出中。"""
        with patch("pyperclip.copy"):
            with patch("bykpy.api.cli.click.echo") as mock_echo:
                copy_to_clipboard("some text", label="CustomLabel")
                assert any(
                    "CustomLabel" in str(call)
                    for call in mock_echo.call_args_list
                )

    def test_missing_pyperclip_raises(self):
        """pyperclip 未安装时抛出 ImportError。"""
        with patch("bykpy.api.cli._require_pyperclip") as mock_guard:
            mock_guard.side_effect = ImportError(
                "pyperclip is required for clipboard operations.\n"
                "Install it with: pip install pyperclip"
            )
            with pytest.raises(ImportError, match="pyperclip is required"):
                copy_to_clipboard("text")


# ── wait_for_server_ready ──────────────────────────────────────────

class TestWaitForServerReady:
    def test_immediate_200(self):
        """服务器立即返回 200。"""
        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_resp = MagicMock()
            mock_resp.status = 200
            mock_urlopen.return_value.__enter__ = MagicMock(return_value=mock_resp)
            mock_urlopen.return_value.__exit__ = MagicMock(return_value=False)
            assert wait_for_server_ready(8080, timeout=1.0) is True

    def test_timeout(self):
        """连接始终失败，最终超时返回 False。"""
        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.side_effect = OSError("Connection refused")
            assert wait_for_server_ready(8080, timeout=0.1) is False

    def test_non_200_then_timeout(self):
        """返回非 200 状态码，继续轮询直到超时。"""
        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_resp = MagicMock()
            mock_resp.status = 500
            mock_urlopen.return_value.__enter__ = MagicMock(return_value=mock_resp)
            mock_urlopen.return_value.__exit__ = MagicMock(return_value=False)
            assert wait_for_server_ready(8080, timeout=0.1) is False

    def test_eventual_success(self):
        """前几次失败，最终成功。"""
        call_count = [0]

        def side_effect(url, timeout=None):
            call_count[0] += 1
            if call_count[0] < 3:
                raise OSError("Connection refused")
            mock_resp = MagicMock()
            mock_resp.status = 200
            cm = MagicMock()
            cm.__enter__ = MagicMock(return_value=mock_resp)
            cm.__exit__ = MagicMock(return_value=False)
            return cm

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.side_effect = side_effect
            assert wait_for_server_ready(8080, timeout=5.0) is True
            assert call_count[0] == 3


# ── open_browser ────────────────────────────────────────────────────

class TestOpenBrowser:
    def test_calls_webbrowser_open(self):
        with patch("webbrowser.open") as mock_open:
            open_browser("http://localhost:8080")
            mock_open.assert_called_once_with("http://localhost:8080")
