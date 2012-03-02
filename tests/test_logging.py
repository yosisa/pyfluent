# -*- coding: utf-8 -*-

import os
import sys
import logging
import socket

import pytest
import msgpack
from mock import MagicMock, Mock, patch, call

import pyfluent.logging
from pyfluent.logging import SafeFluentHandler

_RECORD_CREATED = 1329904180.791739


def pytest_funcarg__record(request):
    record = logging.LogRecord(
        'root', logging.INFO, '/path/to/source.py',
        '10', 'message %d', (1, ), None, 'func_name'
    )
    record.created = _RECORD_CREATED
    return record


class LogRecordCapture(object):
    def __init__(self):
        self.record = None
        handler = logging.Handler()
        handler.setLevel(logging.DEBUG)
        self.logger = logging.getLogger('pytest.fluent')
        self.logger.setLevel(logging.DEBUG)
        self.logger.addFilter(self)

    def __getattr__(self, key):
        if hasattr(self.logger, key):
            return getattr(self.logger, key)
        super(LogRecordCapture, self).__getattr__(key)

    def get(self):
        return self.record

    def filter(self, record):
        self.record = record
        return False


class TestFluentHandler(object):
    @staticmethod
    def pytest_generate_tests(metafunc):
        body = {'message': 'message 1'}
        handler_without_tag = pyfluent.logging.FluentHandler()
        handler_with_tag = pyfluent.logging.FluentHandler(tag='test')
        metafunc.parametrize(('handler', 'expected'), [
            (handler_without_tag, ('info', _RECORD_CREATED, body)),
            (handler_with_tag, ('test.info', _RECORD_CREATED, body)),
        ])

    def test_packing(self, handler, record, expected):
        data = handler.makePickle(record)
        assert msgpack.unpackb(data, encoding='utf-8') == expected


class TestSafeFluentHandler(object):
    def test_queuing(self):
        handler = SafeFluentHandler(capacity=2)
        assert handler.queue == []
        handler.queuing(1)
        assert handler.queue == [1]
        handler.queuing(2)
        assert handler.queue == [1, 2]
        handler.queuing(3)
        assert handler.queue == [2, 3]

    def test_send_normal(self):
        with patch('socket.socket'):
            handler = SafeFluentHandler()
            handler.send('message 1')
            handler.send('message 2')
            calls = [call('message 1'), call('message 2')]
            assert handler.sock.sendall.call_args_list == calls
            assert not handler.queue

    def test_send_fail(self):
        with patch.object(SafeFluentHandler, 'createSocket'):
            handler = SafeFluentHandler()
            handler.send('message 1')
            assert handler.queue == ['message 1']

    def test_send_retransmit(self):
        handler = SafeFluentHandler()
        mock = MagicMock(spec=socket.socket)
        handler.sock = mock
        sendall = handler.sock.sendall
        sendall.side_effect = socket.error()
        handler.send('message 1')
        assert sendall.call_args_list == [call('message 1')]
        assert handler.queue == ['message 1']
        sendall.reset_mock()
        handler.sock = mock
        handler.send('message 2')
        assert sendall.call_args_list == [call('message 1')]
        assert handler.queue == ['message 1', 'message 2']
        sendall.reset_mock()
        sendall.side_effect = None
        handler.sock = mock
        handler.send('message 3')
        assert sendall.call_args_list == [
            call('message 1'), call('message 2'), call('message 3')
        ]
        assert handler.queue == []


class TestFluentFormatter(object):
    hostname = socket.gethostname()
    logger = LogRecordCapture()

    @pytest.mark.parametrize(('key', 'value', 'expected'), [
        ('name', 'root', ('name', 'root')),
        ('levelname', 'INFO', ('levelname', 'info'))
    ])
    def test_prepare(self, key, value, expected):
        fmt = pyfluent.logging.FluentFormatter()
        assert fmt.prepare(key, value) == expected

    def test_format(self, record):
        fmt = pyfluent.logging.FluentFormatter()
        expected = {
            'message': 'message 1',
            'hostname': self.hostname,
            'filename': 'source.py',
            'name': 'root',
            'levelname': 'info',
            'lineno': '10',
            'funcName': 'func_name',
            'exc_text': None,
            'module': 'source',
            'pathname': '/path/to/source.py',
            'process': os.getpid(),
            'processName': 'MainProcess',
            'threadName': 'MainThread'
        }
        if sys.version_info[:3] >= (3, 2, 0):
            expected['stack_info'] = None
        assert fmt.format(record) == expected

    def test_format_with_specify_format(self):
        msg = '%(asctime)s %(levelname)s %(message)s'
        fmt = pyfluent.logging.FluentFormatter(msg)
        self.logger.info('message for test %d', 1)
        data = fmt.format(self.logger.get())
        assert data['name'] == 'pytest.fluent'
        assert data['message'].endswith(' INFO message for test 1')
        assert 'asctime' not in data

    def test_format_with_extra(self):
        fmt = pyfluent.logging.FluentFormatter()
        d = {'additional': 'information'}
        self.logger.info('message for test', extra=d)
        data = fmt.format(self.logger.get())
        assert data['name'] == 'pytest.fluent'
        assert data['message'] == 'message for test'
        assert data['additional'] == 'information'
