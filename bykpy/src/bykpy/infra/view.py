"""根命令仪表盘"""

from __future__ import annotations

import click

from bykpy.core.context import AppContext
from bykpy.infra.cache import load_cache


def render_dashboard(context: AppContext, cli: click.Group) -> None:
    click.echo(cli.get_help(click.Context(cli)))

    # Commands：从缓存读取（零 import）
    cache_data = load_cache(context.paths.cache_dir / "app.json")
    commands = cache_data.get("commands", {})
    if commands:
        cmd_entries = sorted(
            (name, info.get("description", "") if isinstance(info, dict) else str(info))
            for name, info in commands.items()
        )
        click.echo()
        click.echo("Commands:")
        for name, desc in cmd_entries:
            click.echo(f"  ({name}, {desc})")
