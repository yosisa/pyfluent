# -*- coding: utf-8 -*-
# Copyright 2013 Yoshihisa Tanaka
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

import pytest
from mock import MagicMock, patch

from pyfluent import server


@patch.object(server, '_callback')
def test_fluent_callback(cb):
    @server.fluent_callback
    def mycallback(*args):
        pass

    assert server._callback == mycallback


@pytest.mark.parametrize(('bin', 'expected'), [
    ([b"\x92\xa4test\xdb\x00\x00\x00\x14\x92\xceRC\x16'\x81\xa7message\xa4test"],
     [('test', 1380128295, {'message': 'test'})]),
    ([b'\x92\xa4test\xdb\x00\x00\x00*\x92\xceRC\x18\xa6\x81\xa7me'
      b'ssage\xa5hello\x92\xceRC\x18\xa6\x81\xa7message\xa5world'],
     [('test', 1380128934, {'message': 'hello'}),
      ('test', 1380128934, {'message': 'world'})])
])
def test_MessageHandler(bin, expected):
    request = MagicMock()
    request.recv = MagicMock(side_effect=bin+[''])
    results = []
    server.fluent_callback(lambda *args: results.append(args))
    server.MessageHandler(request, None, None)
    assert results == expected


def test_HeartbeatHandler():
    sock = MagicMock()
    server.HeartbeatHandler((None, sock), 'addr', None)
    sock.sendto.assert_called_once_with(server.HEARTBEAT_MSG, 'addr')
