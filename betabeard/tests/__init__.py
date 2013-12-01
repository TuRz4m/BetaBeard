#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from unittest import TextTestRunner, TestSuite

from tests.test_builder import BuilderTestCase
from tests.test_betaseriesapi import BetaSerieAPITestCase


import logging

logging.getLogger(__name__).addHandler(logging.StreamHandler())
logging.getLogger(__name__).setLevel(logging.DEBUG)

suite = TestSuite([BuilderTestCase.suite()])
suite = TestSuite([BetaSerieAPITestCase.suite()])

if __name__ == '__main__':
    TextTestRunner().run(suite)