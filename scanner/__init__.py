"""Network Scanner CLI package

Expose CLI via Click. The package provides subcommands: ping, ports, banner, export
"""

from click import group
from rich.console import Console

console = Console()

@group()
def cli():
    """Network Scanner CLI"""
    pass

from scanner.ping import ping
from scanner.ports import ports

cli.add_command(ping)
cli.add_command(ports)
