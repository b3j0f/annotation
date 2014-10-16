#!/usr/bin/env python
# -*- coding: utf-8 -*-

from b3j0f.annotation.async \
    import Synchronized, Asynchronous, TimeOut, Wait

import unittest


class ThreadingTests(unittest.TestCase):

    def setUp(self):
        pass

    def testSynchronized(self):
        Synchronized
        pass

    def testAsynchronous(self):
        Asynchronous
        pass

    def testTimeOut(self):
        TimeOut
        pass

    def testWait(self):
        Wait
        pass

if __name__ == '__main__':
    unittest.main()
