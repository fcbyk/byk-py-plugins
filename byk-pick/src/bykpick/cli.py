import threading
import click
from bykpy.api import (
    CommandContext,
    check_port,
    copy_to_clipboard,
    echo_network_urls,
    get_private_networks,
    open_browser,
    pass_command_context,
    wait_for_server_ready,
)

from .controller import create_pick_app


def _start_server(app, port: int):
    from waitress import serve
    serve(app, host='0.0.0.0', port=port)


@click.command(name='pick', help='Start web picker server')
@click.option('--port', '-p', default=80, show_default=True, type=int, help='Port for web server')
@click.option('--no-browser', is_flag=True, help='Do not auto-open browser')
@click.option('--files', '-f', type=click.Path(exists=True, dir_okay=True, file_okay=True, readable=True, resolve_path=True), help='Start web file picker with given file/directory')
@click.option('--password', '-pw', is_flag=True, default=False, help='Prompt to set admin password (default: 123456 if not set)')
@pass_command_context
def pick(ctx: CommandContext, port, no_browser, files, password):
    if not check_port(port):
        return

    if password:
        admin_password = click.prompt(
            'Admin password (press Enter to use default: 123456)',
            hide_input=True,
            default='123456',
            show_default=False,
        )
        if not admin_password:
            admin_password = '123456'
    else:
        admin_password = '123456'

    store = ctx.state()
    app = create_pick_app(
        files_root=files,
        admin_password=admin_password,
        state_store=store,
    )

    private_networks = get_private_networks()
    local_ip = private_networks[0]["ips"][0] if private_networks else "127.0.0.1"
    url_network = f"http://{local_ip}:{port}"

    click.echo()
    echo_network_urls(private_networks, port, include_virtual=True)
    click.echo(f" Admin URL: {url_network}/admin")
    if files:
        click.echo(f" Files root: {files}")

    copy_to_clipboard(url_network)
    click.echo()

    if not no_browser:
        server_thread = threading.Thread(
            target=_start_server,
            args=(app, port),
            daemon=True,
        )
        server_thread.start()
        if wait_for_server_ready(port):
            try:
                open_browser(url_network)
                click.echo(" Attempted to open picker page in browser")
            except Exception:
                click.echo(" Note: Could not auto-open browser, please visit the URL above")
        else:
            click.echo(" Note: Server didn't respond in time, please open the URL above manually")
        server_thread.join()
    else:
        _start_server(app, port)
