from __future__ import annotations

import logging
import pytest

from bykpy.api.context import CommandContext
from bykpy.runtime import build_runtime


def test_command_store_is_isolated_per_command(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))

    context = build_runtime()
    hello_store = context.command_store("hello")
    pick_store = context.command_store("pick")

    hello_store.set("count", 3)
    pick_store.set("count", 9)

    assert hello_store.get("count") == 3
    assert pick_store.get("count") == 9
    assert hello_store.path != pick_store.path
    assert hello_store.path.name == "state.json"
    assert hello_store.path.parent == context.paths.state_dir / "hello"


def test_app_store_writes_under_state_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))

    context = build_runtime()
    store = context.store()
    store.set("theme", "light")

    assert store.get("theme") == "light"
    assert store.path == context.paths.state_dir / "byk.config.json"


def test_store_returns_cached_instance(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    context = build_runtime()

    store_a = context.store("shared")
    store_b = context.store("shared")

    assert store_a is store_b


def test_command_store_returns_cached_instance(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    context = build_runtime()

    store_a = context.command_store("server", "state")
    store_b = context.command_store("server", "state")

    assert store_a is store_b


def test_command_context_state_returns_cached_instance(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    context = build_runtime()
    cmd_ctx = CommandContext(name="hello", app=context, logger=logging.getLogger("test"))

    store_a = cmd_ctx.state("cache")
    store_b = cmd_ctx.state("cache")

    assert store_a is store_b


def test_command_store_rejects_path_traversal_name(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    context = build_runtime()

    with pytest.raises(ValueError, match="不能为"):
        context.command_store("..", "state")

    with pytest.raises(ValueError, match="路径分隔符"):
        context.command_store("hello/world", "state")


def test_store_rejects_invalid_name(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    context = build_runtime()

    with pytest.raises(ValueError, match="不能为空"):
        context.store("")

    with pytest.raises(ValueError, match="路径分隔符"):
        context.store("a/b")
