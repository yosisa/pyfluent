# -*- coding: utf-8 -*-

from __future__ import absolute_import

import logging
import logging.handlers
import socket

import msgpack


class FluentHandler(logging.handlers.SocketHandler):
    def __init__(self, host=None, port=24224, tag=None):
        logging.handlers.SocketHandler.__init__(self, host or 'localhost', port)
        self.closeOnError = 1
        self.tag = tag or ''
        self.packer = msgpack.Packer(encoding='utf-8')

    def makePickle(self, record):
        return self.serialize(record)

    def serialize(self, record):
        result = self.format(record)
        if not isinstance(result, dict):
            result = {'message': result}
        tag = ('%s.%s' % (self.tag, record.levelname.lower())).lstrip('.')
        return self.packer.pack([tag, record.created, result])


class SafeFluentHandler(FluentHandler):
    def __init__(self, host=None, port=24224, tag=None, capacity=1000):
        FluentHandler.__init__(self, host, port, tag)
        self.capacity = capacity
        self.queue = []

    def send(self, data):
        if self.sock is None:
            self.createSocket()
        if not self.sock:
            self.queuing(data)
            return
        try:
            while len(self.queue):
                self.sock.sendall(self.queue[0])
                self.queue.pop(0)
            self.sock.sendall(data)
        except socket.error:
            self.queuing(data)
            self.sock.close()
            self.sock = None

    def queuing(self, data):
        self.queue.append(data)
        if self.capacity < len(self.queue):
            self.queue.pop(0)


class FluentFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None):
        logging.Formatter.__init__(self, fmt, datefmt)
        self.exclude = [
            'args', 'asctime', 'created', 'exc_info', 'levelno', 'msecs',
            'msg', 'relativeCreated', 'thread', 'message'
        ]
        self.hostname = socket.gethostname()

    def format(self, record):
        message = logging.Formatter.format(self, record)
        d = {'message': message, 'hostname': self.hostname}
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
