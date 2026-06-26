"""CLI entrypoint for the network scanner package."""

from click import group

from scanner.ping import ping
from scanner.ports import ports
from scanner.scanner import cli_ping


@group()
def cli():
    """Network Scanner CLI."""


cli.add_command(ping)
cli.add_command(ports)
cli.add_command(cli_ping)
