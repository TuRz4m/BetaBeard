#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from unittest import TextTestRunner, TestSuite
from betabeard.tests.test_builder import BuilderTestCase


suite = TestSuite([BuilderTestCase.suite()])


if __name__ == '__main__':
    TextTestRunner().run(suite)