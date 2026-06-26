import ipaddress
import os
import socket
import time
from typing import List, Dict, Optional

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.table import Table

console = Console()

try:
    from scapy.all import ICMP, IP, sr1
except Exception:  # pragma: no cover - scapy can require root privileges
    ICMP = None
    IP = None
    sr1 = None


def _scapy_ready() -> bool:
    """Return True when Scapy is available and usable."""
    return sr1 is not None and ICMP is not None and IP is not None


def _ping_once(ip: str, timeout: float) -> tuple[bool, Optional[float]]:
    """Send one ICMP request and return (alive, response_time_ms)."""
    if not _scapy_ready():
        raise PermissionError(
            "Scapy is not available. This usually means the process lacks the required privileges "
            "for raw ICMP sockets. Try running the command as root or with the appropriate permissions."
        )

    packet = IP(dst=ip) / ICMP()
    start = time.perf_counter()
    try:
        reply = sr1(packet, timeout=timeout, verbose=0)
        elapsed_ms = (time.perf_counter() - start) * 1000
        return reply is not None, round(elapsed_ms, 2)
    except PermissionError:
        raise
    except Exception as exc:
        return False, None


def ping_sweep(subnet: str, timeout: float = 1.0) -> List[Dict[str, object]]:
    """Sweep a subnet with ICMP and return a list of host results.

    Example:
        # python -m scanner.scanner ping 192.168.1.0/24 --timeout 1
    """
    try:
        scapy_ready = _scapy_ready()
    except TypeError:
        scapy_ready = False

    if not scapy_ready:
        raise PermissionError(
            "Scapy requires raw socket privileges for ICMP. Run the command as root or with the required CAP_NET_RAW permissions."
        )

    try:
        network = ipaddress.ip_network(subnet, strict=False)
    except ValueError as exc:
        raise ValueError(f"Invalid subnet: {subnet}") from exc

    hosts = list(network.hosts()) if network.num_addresses > 1 else [network.network_address]
    results: List[Dict[str, object]] = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total}"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task(f"Scanning {subnet}", total=len(hosts))
        for host in hosts:
            ip_str = str(host)
            try:
                result = _ping_once(ip_str, timeout)
                if isinstance(result, tuple):
                    alive, response_time_ms = result
                else:
                    alive = bool(result)
                    response_time_ms = None
            except PermissionError:
                raise
            except Exception:
                alive = False
                response_time_ms = None

            status = "alive" if alive else "down"
            results.append(
                {
                    "ip": ip_str,
                    "status": status,
                    "response_time_ms": response_time_ms,
                }
            )
            progress.update(task, advance=1)

    return results


@click.command(name="ping")
@click.argument("subnet", required=True)
@click.option("--timeout", default=1.0, type=float, show_default=True, help="ICMP timeout in seconds")
def cli_ping(subnet: str, timeout: float):
    """ICMP ping sweep over a subnet using Scapy and Rich."""
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


if __name__ == "__main__":
    cli_ping()  # Example: python -m scanner.scanner 192.168.1.0/24 --timeout 1
