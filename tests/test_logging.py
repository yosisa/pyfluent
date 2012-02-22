# -*- coding: utf-8 -*-

import logging

import pytest
import msgpack

import pyfluent.logging

_RECORD_CREATED = 1329904180.791739


def pytest_funcarg__record(request):
    record = logging.LogRecord(
        'root', logging.INFO, '/path/to/source.py',
        '10', 'message %d', (1, ), None, 'func_name'
    )
    record.created = _RECORD_CREATED
    return record


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
        assert msgpack.unpackb(data) == expected
