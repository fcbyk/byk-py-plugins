# bykpy

[![Python](https://img.shields.io/badge/python-%E2%89%A53.10-blue?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![License](https://img.shields.io/github/license/fcbyk/bykcli.svg)](https://github.com/fcbyk/bykcli/blob/main/LICENSE)

Plugin infrastructure for [bykpy](https://github.com/fcbyk/bykcli).

## Install

```bash
pip install bykpy
```

## Usage

Implement `PluginProtocol` and register your commands:

```python
# my_plugin.py
import click
from bykpy import PluginProtocol

class MyPlugin(PluginProtocol):
    commands = {"hello": "say hello"}

    def register(self, cli: click.Group) -> None:
        @cli.command()
        @click.pass_context
        def hello(ctx):
            click.echo("Hello from my plugin!")
```

## API

- **PluginProtocol** — class-based plugin registration protocol
- **CommandContext / pass_command_context / get_app_context** — command runtime context
- **get_private_networks / ensure_port_available** — network utilities
- **StateStore** — persistent key-value storage per command

## License

MIT
