"""pytest fixtures for bykpy tests."""

from __future__ import annotations

import pytest
from flask import Flask


@pytest.fixture
def app():
    """Flask 测试应用，用于 get_client_ip 等需要请求上下文的测试。"""
    _app = Flask(__name__)
    _app.config["TESTING"] = True
    return _app
