# -*- coding: utf-8 -*-

import time
import socket
from collections import deque

import msgpack


class FluentSender(object):
    def __init__(self, tag, host='localhost', port=24224, timeout=1,
                 capacity=None):
        self.default_tag = tag
        self.host = host
        self.port = port
        self.timeout = timeout
        self._sock = None
        self._reset_retry()
        self._queue = deque(maxlen=capacity)
        self.packer = msgpack.Packer(encoding='utf-8')

    def _reset_retry(self):
        self.retry_time = 0
        self.gs = geometric_sequence()

    @property
    def socket(self):
        if not self._sock:
            self.create_socket()
        return self._sock

    def create_socket(self):
        now = time.time()
        if self.retry_time > now:
            return
        try:
            self._sock = self.make_socket()
            self._reset_retry()
        except socket.error:
            self.retry_time = now + next(self.gs)

    def make_socket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.timeout)
        sock.connect((self.host, self.port))
        return sock

    def send(self, data, tag=None, timestamp=None):
        sock = self.socket
        packed = self._serialize(data, tag, timestamp)
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

    def enqueue(self, data, tag=None, timestamp=None):
        packed = self._serialize(data, tag, timestamp)
        self._queue.append(packed)

    def _serialize(self, data, tag=None, timestamp=None):
        timestamp = timestamp or time.time()
        tag = tag or self.default_tag
        if not isinstance(data, dict):
            data = {'data': data}
        return self.packer.pack([tag, timestamp, data])

    def close(self):
        self._reset_retry()
        if self._sock:
            self._sock.close()
            self._sock = None


def geometric_sequence(start=1.0, factor=2.0, limit=30.0):
    num = start
    while num < limit:
        yield num
        num *= factor
    while True:
        yield limit
