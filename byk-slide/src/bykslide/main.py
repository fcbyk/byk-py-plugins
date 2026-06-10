from bykpy import PluginProtocol

class Plugin(PluginProtocol):

    commands = {
        "slide": "Start PPT remote control server, control slides via mobile web page",
    }

    def register(self, cli):
        from .cli import slide
        cli.add_command(slide)
