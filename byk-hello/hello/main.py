from __future__ import annotations

import click

from .cli import hello, world

def register(cli: click.Group):
    cli.add_command(hello)
    cli.add_command(world)
