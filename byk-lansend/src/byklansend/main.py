from bykpy import PluginProtocol

class Plugin(PluginProtocol):

    commands = {
        "lansend": "Start a local web server for sharing files over LAN",
    }

    def register(self, cli):
        from byklansend.app import lansend
        cli.add_command(lansend)
