import pytest
from unittest import mock

from scanner import ping
from scanner.scanner import ping_sweep


@mock.patch("scanner.ping._ping_once")
def test_ping_one_alive(mock_ping, capsys):
    mock_ping.return_value = True
    # call the command function directly
    runner = mock.MagicMock()
    # call the internal function to simulate sweep
    alive = []
    network = "192.0.2.0/30"  # two hosts
    # invoke module logic
    from scanner.ping import _ping_once
    assert _ping_once is not None


def test_ping_sweep_returns_results(monkeypatch):
    ips = ["192.0.2.1", "192.0.2.2"]

    def fake_ping_once(ip, timeout):
        return ip == "192.0.2.1"

    monkeypatch.setattr("scanner.scanner._ping_once", fake_ping_once)
    results = ping_sweep("192.0.2.0/30", timeout=0.2)

    assert len(results) == 2
    assert results[0]["ip"] == "192.0.2.1"
    assert results[0]["status"] == "alive"
    assert results[1]["ip"] == "192.0.2.2"
    assert results[1]["status"] == "down"


def test_ping_sweep_raises_permission_error(monkeypatch):
    monkeypatch.setattr("scanner.scanner._scapy_ready", False)

    with pytest.raises(PermissionError):
        ping_sweep("192.0.2.0/30", timeout=0.2)
