"""byk-dy 插件入口"""

from bykpy import PluginProtocol


class Plugin(PluginProtocol):
    commands = {
        "dy": "Douyin video parsing and downloading tool.",
    }

    def register(self, cli):
        from .cli import dy

        cli.add_command(dy)
