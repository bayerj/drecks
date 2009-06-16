#! /usr/bin/env python2.6
# -*- coding: utf-8 -*-


__author__ = 'Justin S Bayer, <bayer.justin@googlemail.com>'


import cStringIO as StringIO
import json
import unittest

import drecks


class DrecksTest(unittest.TestCase):

  def setUp(self):
    self.stream = StringIO.StringIO()

  def test_json_reporter(self):
    self.logger = drecks.Logger()
    self.logger.register_reporter(drecks.JsonReporter(stream=self.stream))
    self.logger.log(('error', 'critical'), message='blablabla')
    self.logger.log(('error', 'network'), message='blablabla2')
    data = self.stream.getvalue()
    lines = data.split('\n')
    recovered1 = json.loads(lines[0][5:])
    self.assertEqual(recovered1['labels'], ['error', 'critical'])
    self.assertEqual(recovered1['message'], 'blablabla')
    
    recovered2 = json.loads(lines[1][5:])
    self.assertEqual(recovered2['labels'], ['error', 'network'])
    self.assertEqual(recovered2['message'], 'blablabla2')

  def test_filter(self):
    logger = drecks.Logger()
    r = drecks.ListReporter()
    r.filters.append(lambda l, i, t: 'error' in l)
    logger.register_reporter(r)
    logger.log(('error',), message="foo")
    logger.log(('no-error',), message="foo")
    self.assertEqual(r.items[0][0], ('error',))

  def test_getlogger(self):
    logger1 = drecks.get_logger('one')
    logger2 = drecks.get_logger('one')
    self.assertEqual(id(logger1), id(logger2))
    self.assertEqual(id(drecks._loggers.values()[0]), id(logger1))



if __name__ == '__main__':
  unittest.main()
