Introduction
============
pyfluent is a python client library for `Fluentd <http://fluentd.org/>`_.
It is simple, fast and reliable.

**Notice: since this is early release, the api may change in a future version.**

The primary purpose is to provide pythonic way to transmit JSON message to fluentd.

For better performance, pyfluent connects to fluentd's in_forward plugin and transmit messages that are serialized by MessagePack.
While a connection is failed, messages are automatically queued for latter retransmit.
When a connection is re-established, all queued messages are retransmitted automatically.
So, you don't worry about losing messages.

pyfluent is available under Apache License, Version 2.0.

Installation
============
pyfluent requires python 2.5 or above (include python 3).

You can install using pip::

  $ pip install pyfluent

client
======
Sending message is super simple. Just like this::

  from pyfluent.client import FluentSender
  fluent = FluentSender()
  fluent.send('Hello pyfluent!')

By default, FluentSender connects localhost:24224 and use empty string for tag.
You can change this by passing arguments. ::

  fluent = FluentSender('fluent.example.com', 10000, 'pyfluent')
  fluent.send('Hello pyfluent!')

Above examples, we passed string as argument of FluentSender.send.
For convenience, FluentSender.send make dict automatically before sending.

On the other hand, you can pass dict as argument. ::

  fluent.send({'hello': 'fluent'})

Additionally, you can change tag and timestamp of each message if you want. ::

  import time
  fluent.send({'hello': 'fluent'}, 'pyfluent.info', time.time() - 60)

logging
=======
Since pyfluent logging library implemented like python standard logging library,
it is very easy to introduce pyfluent into existing programs.

Here is a basic usage::

  import logging
  from pyfluent.logging import SafeFluentHandler
  handler = SafeFluentHandler('localhost', 24224, 'pyfluent')
  handler.setLevel(logging.INFO)
  logger = logging.getLogger()
  logger.setLevel(logging.INFO)
  logger.addHandler(handler)
  logger.info('hello pyfluent!')

You can obtain a json message like below through fluentd. ::

  2012-03-02 11:50:46 +0900 pyfluent.info: {"message":"hello pyfluent!"}

As you can see, FluentHandler automatically append log level to the tag.

For convenience, pyfluent provide FluentFormatter to emit more information. ::

  from pyfluent.logging import FluentFormatter
  formatter = FluentFormatter('%(asctime)s %(levelname)s %(message)s')
  handler.setFormatter(formatter)
  logger.info('get more information')

You can obtain a json message like below. ::

  2012-03-02 11:52:18 +0900 pyfluent.info: {"threadName":"MainThread","name":"r
  oot","process":88908,"hostname":"host.example.com","module":"<ipython-input-2
  3-ad36b045792f>","filename":"<ipython-input-23-ad36b045792f>","processName":"
  MainProcess","pathname":"<ipython-input-23-ad36b045792f>","lineno":1,"exc_tex
  t":null,"message":"2012-03-02 12:35:18,321 INFO get more information","funcNa
  me":"<module>","levelname":"info"}

The default behavior is emit all items in __dict__ of LogRecord except ``args``, ``asctime``, ``created``, ``exc_info``, ``levelno``, ``msecs``, ``msg``, ``relativeCreated``, ``thread`` and ``message``. It is customizable if you want, for example, except ``threadName``, ``module``, ``filename``, ``processName``, ``pathname``, ``lineno`` and ``funcName`` in addition to the default. ::

  formatter.exclude += ['threadName', 'module', 'filename', 'process',
  'processName', 'pathname', 'lineno', 'funcName']
  logger.info('suppress unnecessary information')

As a result, you can obtain like below. ::

  2012-03-02 11:54:21 +0900 pyfluent.info: {"exc_text":null,"message":"2012-03-
  02 14:23:21,504 INFO suppress unnecessary information","hostname":"host.examp
  le.com","name":"root","levelname":"info"}

Please note that:

  - ``hostname`` is added automatically by FluentFormatter, so you cannot remove ``hostname`` from output information.
  - ``created`` is converted to the fluentd's time.

History
=======
0.2.0 (2012-04-21)
  - Add FluentSender.
  - Rewrite SafeFluentHandler to use FluentSender internally.
  - Change license to Apache License, Version 2.0 from MIT License.

0.1.2 (2012-03-02)
  - Support python 2.5, 2.6, 3.0, 3.1, 3.2.

0.1.1 (2012-02-26)
  - Fix issue on install from PyPI.

0.1.0 (2012-02-26)
  - First release.
