from bykpy import PluginProtocol


class Plugin(PluginProtocol):
    commands = {
        "ai": " Use OpenAI API to chat in terminal.",
    }

    def register(self, cli):
        from .cli import ai
        cli.add_command(ai)
