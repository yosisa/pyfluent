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
import threading

import msgpack

if sys.version_info[0] < 3:
    import SocketServer as socketserver
else:
    import socketserver


def _do_nothing(data):
    pass

_handler = _do_nothing


def fluent_handler(func):
    global _handler
    _handler = func
    return func


class ThreadingTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True


class UDPServer(socketserver.UDPServer):
    allow_reuse_address = True


class Unpacker(object):
    def __init__(self, callback):
        self.unpacker = msgpack.Unpacker()
        self.callback = callback

    def process(self, data):
        self.unpacker.feed(data)
        for message in self.unpacker:
            self.callback(message)


class MessageHandler(socketserver.BaseRequestHandler):
    def handle(self):
        unpacker = Unpacker(_handler)
        data = self.request.recv(1024)
        while data:
            unpacker.process(data)
            data = self.request.recv(1024)


class HeartbeatHandler(socketserver.BaseRequestHandler):
    def handle(self):
        sock = self.request[1]
        sock.sendto('', self.client_address)


class FluentServer(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def start(self):
        self.msg_server = self._make_msg_server(self.host, self.port)
        self.hb_server = self._make_hb_server(self.host, self.port)
        self.msg_runner = self._start_msg_server(self.msg_server)
        self.hb_runner = self._start_hb_server(self.hb_server)

    def shutdown(self):
        self._shutdown_msg_server(self.msg_server, self.msg_runner)
        self._shutdown_hb_server(self.hb_server, self.hb_runner)

    def _make_msg_server(self, host, port):
        return ThreadingTCPServer((host, port), MessageHandler)

    def _make_hb_server(self, host, port):
        return UDPServer((host, port), HeartbeatHandler)

    def _start_msg_server(self, server):
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        return thread

    def _start_hb_server(self, server):
        return self._start_msg_server(server)

    def _shutdown_msg_server(self, server, runner):
        server.shutdown()

    def _shutdown_hb_server(self, server, runner):
        server.shutdown()


@fluent_handler
def foo(data):
    from pprint import pprint
    pprint(data)


if __name__ == '__main__':
    import time
    sv = FluentServer('0.0.0.0', 10000)
    sv.start()
    try:
        while True:
            time.sleep(0.2)
    except:
        pass
    sv.shutdown()
