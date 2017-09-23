from __future__ import print_function

import sys

LOGLEVEL_QUIET = 0
LOGLEVEL_INFO = 1
LOGLEVEL_DEBUG = 2

LOGLEVEL = LOGLEVEL_DEFAULT = LOGLEVEL_INFO


def log(*args, **kwargs):
  """Prints to stderr with same semantics as print() function.

  Borrowed from: https://stackoverflow.com/a/14981125/19258
  """
  if LOGLEVEL > LOGLEVEL_QUIET:
    print(*args, file=sys.stderr, **kwargs)


def info(*args, **kwargs):
  """Prints to stderr with same semantics as print() function.

  Borrowed from: https://stackoverflow.com/a/14981125/19258
  """
  if LOGLEVEL >= LOGLEVEL_INFO:
    log(*args, **kwargs)


def debug(*args, **kwargs):
  """Prints to stderr with same semantics as print() function.

  Borrowed from: https://stackoverflow.com/a/14981125/19258
  """
  if LOGLEVEL >= LOGLEVEL_DEBUG:
    log(*args, **kwargs)
