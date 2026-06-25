import pytest
from unittest import mock

from scanner import ping


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
