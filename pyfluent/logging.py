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

from __future__ import absolute_import

import logging
import logging.handlers
import socket

import msgpack

from pyfluent.client import ensure_dict


class FluentHandler(logging.handlers.SocketHandler):
    def __init__(self, host='localhost', port=24224, tag=''):
        logging.handlers.SocketHandler.__init__(self, host, port)
        self.tag = tag
        self.closeOnError = 1
        self.packer = msgpack.Packer(encoding='utf-8')

    def makePickle(self, record):
        return self.serialize(record)

    def serialize(self, record):
        result = ensure_dict(self.format(record))
        tag = ('%s.%s' % (self.tag, record.levelname.lower())).lstrip('.')
        return self.packer.pack([tag, record.created, result])


class SafeFluentHandler(FluentHandler):
    def __init__(self, host='localhost', port=24224, tag='', capacity=None):
        FluentHandler.__init__(self, host, port, tag)
        self.capacity = capacity or 1000
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
