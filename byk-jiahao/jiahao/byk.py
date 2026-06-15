from bykpy import PluginProtocol


class Plugin(PluginProtocol):
    commands = {
        "jiahao": "Simulate hacker-style terminal output. All fake, just for show.",
    }

    def register(self, cli):
        from .cli import jiahao
        cli.add_command(jiahao)
