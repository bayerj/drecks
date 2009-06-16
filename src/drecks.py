#! /usr/bin/env python2.6
# -*- coding: utf-8 -*-


__author__ = 'Justin S Bayer, <bayer.justin@googlemail.com>'


import datetime
import json
import Queue
import threading
import sys


def get_logger(name):
  """Return a Logger instance that is defined by a name. 
  
  Create it, if it does not yet exist."""
  if name in _loggers:
    return _loggers[name]
  logger = Logger(name)
  _loggers[name] = logger
  return logger

# Global variable that keeps all the loggers.
_loggers = {}


class Logger(object):
  """Class for logging.

  The threadsafe method log() can be called in order to submit a new log entry.
  This will then be distributed to a number of reporters, which the process the
  entry."""

  def __init__(self, name=None):
    self._reporters = []
    # Lock for logging and adding reporters.
    self._lock = threading.Lock()
    self.name = name

  def log(self, labels, **info):
    """Log an entry. Entry consists of a list of labels and additional keywords.
    A timestamp is generated automatically."""
    timestamp = datetime.datetime.now()
    with self._lock:
      for reporter in self._reporters:
        reporter(labels, info, timestamp)

  def register_reporter(self, reporter):
    """Add a reporter to the internal reporter list.

    The reporter will be called with the arguments (labels, info, timestamp)
    where lables is a list of strings, info is a dictionary containing to be
    logged information and timestamp is a datetime object."""
    with self._lock:
      self._reporters.append(reporter)


def chain(*reporters):
  """Chain multiple reporters together. 

  A reporter can act as a filter by not returning a triple and None instead.
  None will not be passed further along the chain. 
  
  Since the chains are callables themselves, they can be used as any reporter.
  """
  def inner(labels, info, timestamp):
    for r in reporters:
      new = r(labels, info, timestamp)
      if new is None:
        break
      labels, info, timestamp = new
    return labels, info, timestamp
  return inner


class JsonReporter(object):
  """Reporter that logs the information with the usage of json. Every line is
  prefixed be a user defined prefix which (defaults to zero). The log json
  information is also update by the log entries timestamp in the field
  'timestamp' and the labels in the field 'labels'."""

  def __init__(self, stream=sys.stdout, prefix='log> '):
    self.stream = stream
    self.prefix = prefix

  def __call__(self, labels, info, timestamp):
    if 'labels' in info or 'timestamp' in info:
      raise ValueError("fieldnames 'timestamp' and 'labels' in info.")

    # Don't mutate the current dictionary, since it might be used by later
    # reporters.
    dct = info.copy()
    dct.update({'labels': labels,
                 'timestamp': timestamp.isoformat()})

    self.stream.write(self.prefix)
    json.dump(dct, self.stream)
    self.stream.write('\n')

    return labels, info, timestamp
