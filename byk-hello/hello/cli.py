from __future__ import annotations

import click

from bykpy.api import CommandContext, pass_command_context


@click.command(help="Example subcommand to verify dynamic registration.")
@click.option("--name", default="world", show_default=True, help="The object to greet.")
@click.option("--reset-state", is_flag=True, help="Clear hello's local state.")
@pass_command_context
def hello(ctx: CommandContext, name: str, reset_state: bool) -> None:
    # 使用命令专属 logger（默认写入 hello.log）
    ctx.logger.info("hello command executed with name: %s", name)

    store = ctx.state()
    if reset_state:
        ctx.logger.debug("Resetting hello state")
        store.clear()
        click.echo("hello state cleared")
        ctx.logger.info("hello state has been cleared")
        return

    count = int(store.get("run_count", 0)) + 1
    store.update({"run_count": count, "last_name": name})

    click.echo(f"hello {name}")
    click.echo(f"run count: {count}")
    click.echo(f"state file: {store.path}")
    
    # 记录不同级别的日志信息
    ctx.logger.debug("Current run count: %d", count)
    ctx.logger.info("Greeted %s for the %d time(s)", name, count)
    if count > 5:
        ctx.logger.warning("Hello command has been run %d times - consider resetting state", count)
    if count > 10:
        ctx.logger.error("Hello command run count (%d) exceeds recommended limit", count)


@click.command(help="second command")
@pass_command_context
def world(ctx: CommandContext):
    click.echo("second command -> hello world")
