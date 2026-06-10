from bykpy import PluginProtocol

class Plugin(PluginProtocol):
    commands = {
        "hello": " Example subcommand to verify dynamic registration.",
        "world": " Second command to verify dynamic registration.",
    }

    def register(self,cli):
        from .cli import hello, world
        cli.add_command(hello)
        cli.add_command(world)
 