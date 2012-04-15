# -*- coding: utf-8 -*-

import time
import socket

import msgpack
from mock import patch, call

from pyfluent import client


def test_geometric_sequence():
    gs = client.geometric_sequence()
    assert [next(gs) for x in range(8)] == [
        1.0, 2.0, 4.0, 8.0, 16.0, 30.0, 30.0, 30.0
    ]
    gs = client.geometric_sequence(2.0, 1.5, 60.0)
    assert [next(gs) for x in range(8)] == [
        2.0, 3.0, 4.5, 6.75, 10.125, 15.1875, 22.78125, 34.171875
    ]


class TestFluentSender(object):
    def pytest_funcarg__sender(self, request):
        return client.FluentSender('test')

    def test_init(self, sender):
        assert sender.default_tag == 'test'
        assert sender.host == 'localhost'
        assert sender.port == 24224
        assert sender.timeout == 1
        assert sender._retry_time == 0
        assert isinstance(sender.packer, msgpack.Packer)

    def test_make_socket(self, sender):
        with patch('socket.socket'):
            sock = sender._make_socket()
            assert sock.mock_calls == [
                call.settimeout(sender.timeout),
                call.connect((sender.host, sender.port))
            ]

    def test_create_socket(self, sender):
        sender._retry_time = time.time() + 1000
        sender._create_socket()
        assert sender._sock == None
        sender._retry_time = time.time()
        with patch('socket.socket'):
            sender._create_socket()
            assert sender._sock is not None
            assert sender._retry_time == 0
            assert next(sender._wait_time) == 1.0

    def test_create_socket_error(self, sender):
        with patch('socket.socket') as mock:
            mock.side_effect = socket.error
            now = time.time()
            sender._create_socket()
            assert sender._sock is None
            assert now < sender._retry_time < now + 2.0
            assert next(sender._wait_time) == 2.0
