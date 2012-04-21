# -*- coding: utf-8 -*-
# Copyright 2012 Yoshihisa Tanaka
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import with_statement

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
    def pytest_funcarg__handler(self, request):
        handler = pyfluent.logging.SafeFluentHandler()
        handler.fluent = MagicMock(spec=handler.fluent.__class__)
        return handler

    def test_normal(self, handler, record):
        handler.emit(record)
        assert handler.fluent.method_calls == [
            call.send('message 1', 'info', record.created)
        ]

    def test_default_tag(self, record):
        handler = pyfluent.logging.SafeFluentHandler(tag='pyfluent')
        handler.fluent = MagicMock(spec=handler.fluent.__class__)
        handler.emit(record)
        assert handler.fluent.method_calls == [
            call.send('message 1', 'pyfluent.info', record.created)
        ]

    def test_with_formatter(self, handler, record):
        fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        fmt = logging.Formatter(fmt, '%Y-%m-%d %H:%M:%S')
        handler.setFormatter(fmt)
        handler.emit(record)
        message = '2012-02-22 18:49:40 - root - INFO - message 1'
        assert handler.fluent.method_calls == [
            call.send(message, 'info', record.created)
        ]

    def test_close(self, handler):
        with patch('logging.Handler') as mock:
            handler.close()
            assert mock.method_calls == [call.close(handler)]

    def test_handle_error(self, handler, record):
        handler.fluent.send.side_effect = SystemExit
        with pytest.raises(SystemExit):
            handler.emit(record)
        handler.fluent.send.side_effect = KeyboardInterrupt
        with pytest.raises(KeyboardInterrupt):
            handler.emit(record)
        handler.fluent.send.side_effect = Exception
        mock = Mock()
        handler.handleError = mock
        handler.emit(record)
        assert mock.call_args_list == [call(record)]


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
        if sys.version_info[:3] < (2, 6, 0) or sys.version_info[:2] == (3, 0):
            del expected['processName']
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
