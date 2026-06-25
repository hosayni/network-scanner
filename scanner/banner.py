import socket
from typing import Optional

import click
from rich.console import Console

console = Console()

@click.command()
@click.argument("host")
@click.argument("port", type=int)
@click.option("-t", "--timeout", default=2.0, help="Receive timeout")
def banner(host: str, port: int, timeout: float):
    """Retrieve service banner for a TCP service"""
    b = _grab_banner(host, port, timeout)
    if b:
        console.print(f"[green]{host}:{port} banner:[/green]\n[b]{b}[/b]")
    else:
        console.print(f"No banner for {host}:{port}")


def _grab_banner(host: str, port: int, timeout: float) -> Optional[str]:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((host, port))
        try:
            s.sendall(b"\r\n")
            data = s.recv(4096)
            return data.decode(errors="ignore").strip()
        except Exception:
            return None
        finally:
            s.close()
    except Exception:
        return None
