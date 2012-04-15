# -*- coding: utf-8 -*-

import time
import socket

import msgpack
import pytest
from mock import MagicMock, patch, call

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

    def pytest_funcarg__msgs(self, request):
        return [
            {'message': 'test1'}, {'message': 'test2'}, {'message': 'test3'}
        ]

    def test_init(self, sender):
        assert sender.default_tag == 'test'
        assert sender.host == 'localhost'
        assert sender.port == 24224
        assert sender.timeout == 1
        assert sender._retry_time == 0
        assert sender._queue.maxlen == None
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

    def test_get_socket(self, sender):
        with patch('socket.socket'):
            assert sender._sock is None
            sock1 = sender.socket
            assert sock1 is not None
            assert sender._sock is sock1
            sock2 = sender.socket
            assert sock1 is sock2

    def test_close(self, sender):
        sender.close()
        assert sender._retry_time == 0
        assert next(sender._wait_time) == 1.0
        mock = sender._sock = MagicMock(spec=socket.socket)
        sender.close()
        assert mock.method_calls == [call.close()]
        assert sender._sock == None
        assert sender._retry_time == 0
        assert next(sender._wait_time) == 1.0

    def test_serialize_default_args(self, sender):
        now = time.time()
        r1 = sender.serialize('test data')
        r2 = sender.serialize({'message': 'test'})
        r1 = msgpack.unpackb(r1)
        r2 = msgpack.unpackb(r2)
        assert r1[0] == r2[0] == sender.default_tag
        assert now < r1[1] <= r2[1] < now + 2
        assert r1[2] == {'data': 'test data'}
        assert r2[2] == {'message': 'test'}

    def test_serialize(self, sender):
        data = {'string': 'test', 'number': 10}
        tag = 'pyfluent.test'
        timestamp = time.time()
        r = sender.serialize(data, tag, timestamp)
        assert msgpack.unpackb(r) == (tag, timestamp, data)

    def test_send_normal(self, sender, msgs):
        with patch('socket.socket'):
            timestamp = time.time()
            f = lambda d: msgpack.packb([sender.default_tag, timestamp, d])
            sender.send(msgs[0], timestamp=timestamp)
            sender.send(msgs[1], timestamp=timestamp)
            assert sender._sock.sendall.call_args_list == [
                call(f(msgs[0])), call(f(msgs[1]))
            ]
            assert len(sender._queue) == 0

    def test_send_fail(self, sender, msgs):
        with patch('socket.socket') as mock:
            mock.side_effect = socket.error
            timestamp = time.time()
            f = lambda d: msgpack.packb([sender.default_tag, timestamp, d])
            sender.send(msgs[0], timestamp=timestamp)
            sender.send(msgs[1], timestamp=timestamp)
            list(sender._queue) == [f(msgs[0]), f(msgs[1])]

    def test_send_retransmit(self, sender, msgs):
        mock = MagicMock(spec=socket.socket)
        sender._sock = mock
        sendall = sender._sock.sendall
        sendall.side_effect = socket.error
        timestamp = time.time()
        f = lambda d: msgpack.packb([sender.default_tag, timestamp, d])
        # try 1 then fail
        sender.send(msgs[0], timestamp=timestamp)
        assert sendall.call_args_list == [call(f(msgs[0]))]
        assert list(sender._queue) == [f(msgs[0])]
        assert sender._sock == None
        # try 2 then fail
        sender._sock = mock
        sendall.reset_mock()
        sender.send(msgs[1], timestamp=timestamp)
        assert sendall.call_args_list == [call(f(msgs[0]))]
        assert list(sender._queue) == [f(msgs[0]), f(msgs[1])]
        assert sender._sock == None
        # try 3 then success
        sender._sock = mock
        sendall.reset_mock()
        sendall.side_effect = None
        sender.send(msgs[2], timestamp=timestamp)
        assert sendall.call_args_list == [call(f(msgs[x])) for x in range(3)]
        assert len(sender._queue) == 0
