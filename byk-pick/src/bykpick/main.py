from bykpy import PluginProtocol


class Plugin(PluginProtocol):

    commands = {
        "pick": "Start web picker server for random selection and file lottery.",
    }

    def register(self, cli):
        from .cli import pick
        cli.add_command(pick)
