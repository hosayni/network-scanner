import socket
import click
from rich.table import Table
from rich.console import Console
from typing import List

console = Console()

@click.command()
@click.argument("host")
@click.option("-p", "--ports", default="1-1024", help="Port range, e.g. 22,80,8000-8100")
@click.option("-t", "--timeout", default=1.0, help="Connect timeout")
def ports(host: str, ports: str, timeout: float):
    """Simple TCP port scanner"""
    port_list = _parse_ports(ports)
    open_ports = []
    for port in port_list:
        if _tcp_connect(host, port, timeout):
            open_ports.append(port)
            console.print(f"[green]{host}:{port} open[/green]")
        else:
            console.print(f"{host}:{port} closed", style="dim")

    if open_ports:
        table = Table(title=f"Open ports on {host}")
        table.add_column("Port", justify="right")
        table.add_column("Service")
        for p in open_ports:
            try:
                service = socket.getservbyport(p)
            except Exception:
                service = "unknown"
            table.add_row(str(p), service)
        console.print(table)


def _parse_ports(ports: str) -> List[int]:
    out = set()
    for part in ports.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            for i in range(int(a), int(b) + 1):
                out.add(i)
        else:
            out.add(int(part))
    return sorted(out)


def _tcp_connect(host: str, port: int, timeout: float) -> bool:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((host, port))
        s.close()
        return True
    except Exception:
        return False
