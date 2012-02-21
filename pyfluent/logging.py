# -*- coding: utf-8 -*-

from __future__ import absolute_import

import logging
import logging.handlers

import msgpack


class FluentHandler(logging.handlers.SocketHandler):
    def __init__(self, host=None, port=24224, tag=None):
        super(FluentHandler, self).__init__(host or 'localhost', port)
        self.closeOnError = 1
        self.tag = tag or ''
        self.packer = msgpack.Packer()

    def makePickle(self, record):
        return self.serialize(record)

    def serialize(self, record):
        result = self.format(record)
        if not isinstance(result, dict):
            result = {'message': result}
        tag = ('%s.%s' % (self.tag, record.levelname.lower())).lstrip('.')
        return self.packer.pack([tag, record.created, result])


class FluentFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None):
        super(FluentFormatter, self).__init__(fmt, datefmt)
        self.exclude = [
            'args', 'asctime', 'created', 'exc_info', 'levelno', 'msecs',
            'msg', 'relativeCreated', 'thread'
        ]

    def format(self, record):
        message = super(FluentFormatter, self).format(record)
        d = {'message': message}
        for key in record.__dict__.keys():
            if key in self.exclude:
                continue
            value = getattr(record, key)
            try:
                key, value = self.prepare(key, value)
            except:
                pass
            d[key] = value
        return d

    def prepare(self, key, value):
        if key == 'levelname':
            return key, value.lower()
        return key, value
