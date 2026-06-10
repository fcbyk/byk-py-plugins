"""CLI 应用装配。"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import click

from bykpy.core.context import AppContext
from bykpy.core.errors import CliError

logger = logging.getLogger("bykpy")


def _resolve_log_path(ctx: click.Context) -> str:
    """解析日志文件绝对路径，提供健壮的 fallback。"""
    try:
        if ctx.obj is not None:
            paths = ctx.obj.context.paths
            if paths is not None:
                return str(paths.app_log_file)
    except Exception:
        pass

    # 运行时未初始化时的备选路径
    return str(Path.home() / ".byk" / "logs" / "app.log")


class PluginAwareGroup(click.Group):
    """支持插件动态加载的命令组。"""

    runtime_provider: Any = None

    def parse_args(self, ctx: click.Context, args: list[str]) -> list[str]:
        return super().parse_args(ctx, args)

    def resolve_command(
        self,
        ctx: click.Context,
        args: list[str],
    ) -> tuple[str | None, click.Command | None, list[str]]:
        orig_args = list(args)
        try:
            return super().resolve_command(ctx, args)
        except click.UsageError:
            pass

        if not orig_args:
            return super().resolve_command(ctx, orig_args)

        context = self._get_context(ctx)

        # 检查缓存中的插件命令，按需加载单个插件
        from bykpy.infra.cache import load_cache
        from bykpy.infra.registry import load_single_plugin

        cache_data = load_cache(context.paths.cache_dir / "app.json")
        if orig_args[0] in cache_data.get("commands", {}):
            cmd_name = orig_args[0]
            module_path = cache_data["commands"][cmd_name]["module"]
            load_single_plugin(self, cmd_name, module_path)
            return super().resolve_command(ctx, orig_args)

        # 未知命令
        raise click.UsageError(f"Unknown command: {orig_args[0]}")

    def _get_context(self, ctx: click.Context) -> AppContext:
        """在命令解析阶段获取运行时上下文。"""
        if ctx.obj is not None:
            return ctx.obj.context
        if callable(self.runtime_provider):
            return self.runtime_provider()  # type: ignore[return-type]
        raise click.ClickException("Runtime context not yet initialized")

    def invoke(self, ctx: click.Context) -> Any:
        """统一兜底未处理异常"""
        try:
            return super().invoke(ctx)
        except click.ClickException:
            raise
        except click.exceptions.Exit:
            raise
        except CliError as exc:
            logger.warning("cli error: %s", exc)
            raise click.ClickException(str(exc)) from exc
        except SystemExit:
            raise
        except Exception as exc:  # noqa: BLE001
            logger.exception("unexpected cli error")
            log_file = _resolve_log_path(ctx)
            raise click.ClickException(
                f"Unexpected error occurred, see logs at: {log_file}"
            ) from exc


@dataclass(slots=True)
class CliState:
    """Click 根命令共享状态。"""

    context: AppContext


def version_callback(
    ctx: click.Context,
    _param: click.Parameter,
    value: bool,
) -> None:
    """Show version and exit."""
    if not value or ctx.resilient_parsing:
        return

    from bykpy.runtime import build_runtime

    app_context: AppContext = ctx.obj.context if ctx.obj else build_runtime()
    click.echo(f"v{app_context.version}")
    ctx.exit()


def create_cli() -> click.Group:
    """创建根 CLI 对象。"""

    from bykpy.runtime import build_runtime

    runtime: AppContext | None = None

    def get_runtime() -> AppContext:
        nonlocal runtime
        if runtime is None:
            runtime = build_runtime()
        return runtime

    @click.group(
        cls=PluginAwareGroup,
        context_settings={"help_option_names": ["-h", "--help"]},
        add_help_option=False,
        invoke_without_command=True,
    )
    @click.option(
        "--version",
        "-v",
        is_flag=True,
        callback=version_callback,
        expose_value=False,
        is_eager=True,
        help="Show version and exit.",
    )
    @click.pass_context
    def cli(ctx: click.Context) -> None:
        ctx.obj = CliState(context=get_runtime())
        ctx.obj.context.logger.info("BYK v%s started", ctx.obj.context.version)
        if ctx.invoked_subcommand is None:
            from bykpy.infra.view import render_dashboard

            render_dashboard(ctx.obj.context, cli)

    cli.runtime_provider = get_runtime
    return cli
