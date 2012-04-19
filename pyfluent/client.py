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

import sys
import time
import socket
from collections import deque

import msgpack

if sys.version_info[:2] <= (2, 5):
    next = lambda iter: iter.next()


class FluentSender(object):
    def __init__(self, host='localhost', port=24224, tag='',
                 timeout=1, capacity=None):
        self.host = host
        self.port = port
        self.tag = tag
        self.timeout = timeout
        self.capacity = capacity
        self._sock = None
        self._reset_retry()
        self._queue = self._make_queue()
        self.packer = msgpack.Packer(encoding='utf-8')

    def _reset_retry(self):
        self._retry_time = 0
        self._wait_time = geometric_sequence()

    def _make_queue(self):
        if sys.version_info[:2] <= (2, 5):
            return deque()
        return deque(maxlen=self.capacity)

    @property
    def socket(self):
        if not self._sock:
            self._create_socket()
        return self._sock

    def _create_socket(self):
        now = time.time()
        if self._retry_time > now:
            return
        try:
            self._sock = self._make_socket()
            self._reset_retry()
        except socket.error:
            self._retry_time = now + next(self._wait_time)

    def _make_socket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.timeout)
        sock.connect((self.host, self.port))
        return sock

    def send(self, data, tag=None, timestamp=None):
        sock = self.socket
        packed = self.serialize(data, tag, timestamp)
        if not sock:
            self._queue.append(packed)
            return
        try:
            while len(self._queue):
                sock.sendall(self._queue[0])
                self._queue.popleft()
            sock.sendall(packed)
        except socket.error:
            self._queue.append(packed)
            self.close()

    def serialize(self, data, tag=None, timestamp=None):
        timestamp = timestamp or time.time()
        tag = tag or self.tag
        data = ensure_dict(data)
        return self.packer.pack([tag, timestamp, data])

    def close(self):
        self._reset_retry()
        if self._sock:
            self._sock.close()
            self._sock = None


def ensure_dict(data):
    if isinstance(data, dict):
        return data
    return {'message': data}


def geometric_sequence(start=1.0, factor=2.0, limit=30.0):
    num = start
    while num < limit:
        yield num
        num *= factor
    while True:
        yield limit
