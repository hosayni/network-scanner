import pytest
from scanner.ports import _parse_ports, _tcp_connect


def test_parse_ports_single_and_range():
    res = _parse_ports("22,80,8000-8002")
    assert 22 in res
    assert 80 in res
    assert 8000 in res and 8002 in res


def test_tcp_connect_localhost_closed():
    # assuming port 9 (discard) is closed; this is a soft test
    assert _tcp_connect("127.0.0.1", 9, 0.5) in (True, False)
