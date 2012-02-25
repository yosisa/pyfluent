Introduction
============
pyfluent is a python library for `Fluentd <http://fluentd.org/>`_.

**Notice: since this is very early release, the api may change on a future version.**

The primary purpose is to provide pythonic way to transmit JSON message to fluentd.

pyfluent has these features.

- Simplicity: easy to use interface.
- Consistency: a message is not lost even if a connection is lost.
- Speed: using MessagePack and directly connect to fluentd's in_forward plugin.

usage
=====
Since pyfluent logging library implemented like python standard logging library,
It is very easy to introduce pyfluent into existing programs.

Here is a basic usage::

  import logging
  import pyfluent.logging
  host = 'localhost'
  port = 24224
  tag = 'pyfluent'
  handler = pyfluent.logging.SafeFluentHandler(host, port, tag)
  handler.setLevel(logging.INFO)
  logger = logging.getLogger()
  logger.setLevel(logging.INFO)
  logger.addHandler(handler)
  logger.info('hello pyfluent!')
