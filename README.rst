Introduction
============
pyfluent is a python client library for `Fluentd <http://fluentd.org/>`_.
It is simple, fast and reliable, yet powerful.

**Notice: since this is very early release, the api may change on a future version.**

The primary purpose is to provide pythonic way to transmit JSON message to fluentd.

For better performance, pyfluent connects to fluentd's in_forward plugin and transmit messages that are serialized by MessagePack. When a connection is failed, messages are queued. And a connection is re-established, queued messages are retransmitted automatically. So, you don't worry about losing messages.

pyfluent distributed under MIT license.

Installation
============
pyfluent requires python 2.5 or above (include python 3).

You can install using pip::

  $ pip install pyfluent

Example
=======
Since pyfluent logging library implemented like python standard logging library,
It is very easy to introduce pyfluent into existing programs.

Here is a basic usage::

  >>> import logging
  >>> from pyfluent.logging import SafeFluentHandler
  >>> handler = SafeFluentHandler('localhost', 24224, 'pyfluent')
  >>> handler.setLevel(logging.INFO)
  >>> logger = logging.getLogger()
  >>> logger.setLevel(logging.INFO)
  >>> logger.addHandler(handler)
  >>> logger.info('hello pyfluent!')

You can obtain a json message like below through fluentd. ::

  2012-03-02 11:50:46 +0900 pyfluent.info: {"message":"hello pyfluent!"}

As you can see, FluentHandler automatically append log level to the tag.

For convenience, pyfluent provide FluentFormatter to emit more information. ::

  >>> from pyfluent.logging import FluentFormatter
  >>> formatter = FluentFormatter('%(asctime)s %(levelname)s %(message)s')
  >>> handler.setFormatter(formatter)
  >>> logger.info('get more information')

You can obtain a json message like below. ::

  2012-03-02 11:52:18 +0900 pyfluent.info: {"threadName":"MainThread","name":"r
  oot","process":88908,"hostname":"host.example.com","module":"<ipython-input-2
  3-ad36b045792f>","filename":"<ipython-input-23-ad36b045792f>","processName":"
  MainProcess","pathname":"<ipython-input-23-ad36b045792f>","lineno":1,"exc_tex
  t":null,"message":"2012-03-02 12:35:18,321 INFO get more information","funcNa
  me":"<module>","levelname":"info"}

The default behavior is emit all items in __dict__ of LogRecord except ``args``, ``asctime``, ``created``, ``exc_info``, ``levelno``, ``msecs``, ``msg``, ``relativeCreated``, ``thread`` and ``message``. It is customizable if you want, for example, except ``threadName``, ``module``, ``filename``, ``processName``, ``pathname``, ``lineno`` and ``funcName`` in addition to the default. ::

  >>> formatter.exclude += ['threadName', 'module', 'filename', 'process',
  ... 'processName', 'pathname', 'lineno', 'funcName']
  >>> logger.info('suppress unnecessary information')

As a result, you can obtain like below. ::

  2012-03-02 11:54:21 +0900 pyfluent.info: {"exc_text":null,"message":"2012-03-
  02 14:23:21,504 INFO suppress unnecessary information","hostname":"host.examp
  le.com","name":"root","levelname":"info"}

Please note that:

  - ``hostname`` is added automatically by FluentFormatter, so you cannot remove ``hostname`` from output information.
  - ``created`` is converted to the fluentd's time.

History
=======
0.1.2 (2012-03-02)
  - support python 2.5, 2.6, 3.0, 3.1, 3.2

0.1.1 (2012-02-26)
  - fix issue on install from PyPI

0.1.0 (2012-02-26)
  - first release
