import click
from typing import Any
from bykpy.api import ensure_port_available


def check_port(port: int, host: str = "0.0.0.0", output_prefix: str = " ", silent: bool = False) -> bool:
    try:
        ensure_port_available(port=port, host=host)
    except OSError as e:
        if not silent:
            click.echo(
                f"{output_prefix}Error: Port {port} is already in use (or you don't have permission). "
                f"{output_prefix}Please choose another port (e.g. --port {int(port) + 1})."
            )
            click.echo(f"{output_prefix}Details: {e}\n")
        return False
    return True


def colored_key_value(key: str, value: Any, key_color: str = 'cyan', value_color: str = 'yellow') -> str:
    return f"{click.style(str(key), fg=key_color)}: {click.style(str(value), fg=value_color)}"


def echo_network_urls(networks: list, port: int, include_virtual: bool = False):
    for host in ["localhost", "127.0.0.1"]:
        click.echo(colored_key_value(" Local", f"http://{host}:{port}", key_color=None, value_color="cyan"))

    for net in networks:
        if net['virtual'] and not include_virtual:
            continue

        for ip in net["ips"]:
            if ip == "127.0.0.1":
                continue
            click.echo(colored_key_value(f" [{net['iface']}] Network URL:", f"http://{ip}:{port}", key_color=None, value_color="cyan"))


def wait_for_server_ready(port: int, host: str = "127.0.0.1", timeout: float = 10.0) -> bool:
    import time
    import urllib.error
    import urllib.request

    url = f"http://{host}:{port}/"
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=0.5) as resp:
                if resp.status == 200:
                    return True
        except (urllib.error.URLError, TimeoutError, OSError):
            pass
        time.sleep(0.05)
    return False


def copy_to_clipboard(text: str, label: str = "URL", output_prefix: str = " ", silent: bool = False):
    import pyperclip
    import click
    
    try:
        pyperclip.copy(text)
        if not silent:
            click.echo(f"{output_prefix}{label} has been copied to clipboard")
    except Exception:
        if not silent:
            click.echo(f"{output_prefix}Warning: Could not copy {label} to clipboard")
