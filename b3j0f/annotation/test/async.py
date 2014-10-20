#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import main

from b3j0f.utils.ut import UTCase
from b3j0f.annotation.async import Synchronized, Asynchronous, TimeOut, Wait


class ThreadingTests(UTCase):

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
    main()
