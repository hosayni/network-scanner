import ipaddress
import json
import time
from typing import List

import click
from rich.table import Table
from rich.console import Console

console = Console()

try:
    from scapy.all import ICMP, IP, sr1
except Exception:  # pragma: no cover
    # scapy may require root privileges; tests can mock functions
    ICMP = None
    IP = None
    sr1 = None


@click.command(name="ping")
@click.argument("network", required=False)
@click.option("--subnet", type=str, help="Subnet to sweep in CIDR notation")
@click.option("-t", "--timeout", default=1.0, help="ICMP timeout in seconds")
@click.option("-o", "--output", type=click.Choice(["json", "csv", "none"]), default="none")
def ping(network: str | None, subnet: str | None, timeout: float, output: str):
    """ICMP ping sweep of a network or subnet."""
    from scanner.scanner import ping_sweep

    if subnet:
        try:
            results = ping_sweep(subnet, timeout=timeout)
        except PermissionError as exc:
            console.print(f"[bold red]Permission error:[/bold red] {exc}")
            raise click.Abort() from exc
        except ValueError as exc:
            console.print(f"[bold red]{exc}[/bold red]")
            raise click.Abort() from exc

        table = Table(title=f"ICMP sweep results for {subnet}")
        table.add_column("IP", style="cyan")
        table.add_column("Status", style="magenta")
        table.add_column("Response time (ms)", justify="right")
        for entry in results:
            status = entry["status"]
            response = entry["response_time_ms"]
            if status == "alive":
                table.add_row(entry["ip"], "[green]alive[/green]", str(response) if response is not None else "n/a")
            else:
                table.add_row(entry["ip"], "[red]down[/red]", "-" if response is None else str(response))
        console.print(table)
        return

    if not network:
        raise click.UsageError("Provide a network argument or use --subnet")

    try:
        net = ipaddress.ip_network(network, strict=False)
    except Exception as e:
        console.print(f"[red]Invalid network:[/red] {e}")
        raise click.Abort()

    alive = []
    for ip in net.hosts():
        ip_str = str(ip)
        alive_flag = _ping_once(ip_str, timeout)
        if alive_flag:
            alive.append(ip_str)
            console.print(f"[green]{ip_str} is alive[/green]")
        else:
            console.print(f"{ip_str} is down", style="dim")

    if output == "json":
        console.print(json.dumps({"alive": alive}, indent=2))
    elif output == "csv":
        console.print("ip")
        for a in alive:
            console.print(a)


def _ping_once(ip: str, timeout: float) -> bool:
    """Send a single ICMP echo request. Return True if reply received."""
    if sr1 is None:
        # Not running scapy environment; fall back to system ping
        import subprocess

        try:
            proc = subprocess.run(["ping", "-c", "1", "-W", str(int(timeout)), ip], stdout=subprocess.DEVNULL)
            return proc.returncode == 0
        except Exception:
            return False

    pkt = IP(dst=ip) / ICMP()
    try:
        reply = sr1(pkt, timeout=timeout, verbose=0)
        return reply is not None
    except Exception:
        return False
