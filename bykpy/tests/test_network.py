from __future__ import annotations

import socket
from unittest.mock import MagicMock, patch

import pytest

from bykpy.api.network import (
    detect_iface_type,
    ensure_port_available,
    get_private_networks,
)


class TestDetectIfaceType:
    def test_vmware_interface(self):
        result = detect_iface_type("vmware0")
        assert result == ("vmware", True, 30)

    def test_vmnet_interface(self):
        result = detect_iface_type("vmnet1")
        assert result == ("vmware", True, 30)

    def test_vbox_interface(self):
        result = detect_iface_type("vboxnet0")
        assert result == ("virtualbox", True, 30)

    def test_virtualbox_interface(self):
        result = detect_iface_type("virtualbox0")
        assert result == ("virtualbox", True, 30)

    def test_docker_interface(self):
        result = detect_iface_type("docker0")
        assert result == ("container", True, 40)

    def test_wsl_interface(self):
        result = detect_iface_type("wsl")
        assert result == ("container", True, 40)

    def test_bluetooth_interface(self):
        result = detect_iface_type("bluetooth0")
        assert result == ("bluetooth", True, 60)

    def test_ethernet_interface(self):
        result = detect_iface_type("ethernet0")
        assert result == ("ethernet", False, 10)

    def test_chinese_ethernet_interface(self):
        result = detect_iface_type("以太网")
        assert result == ("ethernet", False, 10)

    def test_wlan_interface(self):
        result = detect_iface_type("wlan0")
        assert result == ("wifi", False, 10)

    def test_wifi_interface(self):
        result = detect_iface_type("wi-fi")
        assert result == ("wifi", False, 10)

    def test_chinese_wifi_interface(self):
        result = detect_iface_type("无线网络")
        assert result == ("wifi", False, 10)

    def test_loopback_interface(self):
        result = detect_iface_type("loopback0")
        assert result == ("loopback", True, 100)

    def test_unknown_interface(self):
        result = detect_iface_type("unknown0")
        assert result == ("unknown", False, 50)

    def test_case_insensitive(self):
        result = detect_iface_type("DOCKER0")
        assert result == ("container", True, 40)


class TestGetPrivateNetworks:
    def test_import_error_returns_localhost(self):
        """psutil 导入失败时返回 localhost。"""
        import builtins
        _orig_import = builtins.__import__

        def _mock_import(name, *args, **kwargs):
            if name == "psutil":
                raise ImportError("No module named 'psutil'")
            return _orig_import(name, *args, **kwargs)

        builtins.__import__ = _mock_import
        try:
            result = get_private_networks()
            assert len(result) == 1
            assert result[0]["iface"] == "localhost"
            assert result[0]["ips"] == ["127.0.0.1"]
        finally:
            builtins.__import__ = _orig_import


class TestEnsurePortAvailable:
    def test_port_available(self):
        with patch("socket.socket") as mock_socket_class:
            mock_socket = MagicMock()
            mock_socket_class.return_value.__enter__ = MagicMock(return_value=mock_socket)
            mock_socket_class.return_value.__exit__ = MagicMock(return_value=False)
            ensure_port_available(8080)
            mock_socket.bind.assert_called_once_with(("0.0.0.0", 8080))

    def test_custom_host(self):
        with patch("socket.socket") as mock_socket_class:
            mock_socket = MagicMock()
            mock_socket_class.return_value.__enter__ = MagicMock(return_value=mock_socket)
            mock_socket_class.return_value.__exit__ = MagicMock(return_value=False)
            ensure_port_available(3000, host="127.0.0.1")
            mock_socket.bind.assert_called_once_with(("127.0.0.1", 3000))

    def test_port_as_string(self):
        with patch("socket.socket") as mock_socket_class:
            mock_socket = MagicMock()
            mock_socket_class.return_value.__enter__ = MagicMock(return_value=mock_socket)
            mock_socket_class.return_value.__exit__ = MagicMock(return_value=False)
            ensure_port_available("8080")  # type: ignore[arg-type]
            mock_socket.bind.assert_called_once_with(("0.0.0.0", 8080))

    def test_socket_options_set(self):
        with patch("socket.socket") as mock_socket_class:
            mock_socket = MagicMock()
            mock_socket_class.return_value.__enter__ = MagicMock(return_value=mock_socket)
            mock_socket_class.return_value.__exit__ = MagicMock(return_value=False)
            ensure_port_available(8080)
            mock_socket.setsockopt.assert_called_once_with(
                socket.SOL_SOCKET, socket.SO_REUSEADDR, 1
            )
