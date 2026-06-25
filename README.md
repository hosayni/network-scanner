# Network Scanner

[![CI](https://github.com/youruser/network-scanner/actions/workflows/ci.yml/badge.svg)](https://github.com/youruser/network-scanner/actions/workflows/ci.yml)
[![Coverage](https://coveralls.io/repos/github/youruser/network-scanner/badge.svg)](https://coveralls.io/github/youruser/network-scanner)

Simple network scanner CLI using Python, Scapy, Click and Rich.

Features
- ICMP ping sweep
- TCP port scanning
- Service banner grabbing
- Export to JSON/CSV

Quickstart

Install dependencies:

```bash
pip install -r requirements.txt
```

Usage examples:

Ping sweep a /30 network:

```bash
python -m scanner ping 192.0.2.0/30
```

Scan common ports on a host:

```bash
python -m scanner ports 192.0.2.1 --ports 22,80,443
```

Export results to JSON (example using the library functions):

```python
from scanner import export
export.to_json({"alive": ["192.0.2.1"]}, "out.json")
```

License

MIT
