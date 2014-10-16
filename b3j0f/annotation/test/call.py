#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from b3j0f.annotation.interception import Interceptor
from b3j0f.annotation.check import Condition
from b3j0f.annotation.call import Types, Curried, Retries


class CallTests(unittest.TestCase):

    def setUp(self):
        pass

    def _assertCall(self, f, *args, **kwargs):

        e = None

        try:
            f(*args, **kwargs)
        except Exception as e:
            pass

        self.assertTrue(e is not None)

    def testTypes(self):

        @Types(result_type=int)
        def a(p=None):
            return p

        a(1)
        a()
        self._assertCall(a, '')

        @Types(result_type=Types.NotNone(int))
        def b(p=None):
            return p

        b(2)
        self._assertCall(b, '')
        self._assertCall(b)

        @Types(result_type=[int])
        def c(p=None):
            return [2, 3] \
                if p == 1 else \
                None if p == 2 else \
                [] if p == 3 else \
                [2, None] if p == 4 else [2, '']

        c(1)
        c(2)
        c(3)
        c(4)
        self._assertCall(c)

        @Types([Types.NotNone(int)])
        def d(p=None):
            return [2, 3] \
                if p == 1 else \
                None if p == 2 else \
                [] if p == 3 else \
                [2, None] if p == 4 else [2, '']

        d(1)
        d(2)
        d(3)
        self._assertCall(d, 4)
        self._assertCall(d)

        @Types(Types.NotEmpty([int]))
        def e(p=None):
            return [2, 3] \
                if p == 1 else \
                None if p == 2 else \
                [] if p == 3 else \
                [2, None] if p == 4 else [2, '']

        e(1)
        e(2)
        self._assertCall(e, 3)
        e(4)
        self._assertCall(e)

        @Types(Types.NotEmpty([Types.NotNone(int)]))
        def f(p=None):
            return [2, 3] \
                if p == 1 else \
                None if p == 2 else \
                [] if p == 3 else \
                [2, None] if p == 4 else [2, '']

        f(1)
        f(2)
        self._assertCall(f, 3)
        self._assertCall(f, 4)
        self._assertCall(f)

        @Types(Types.NotNone(Types.NotEmpty([int])))
        def g(p=None):
            return [2, 3] \
                if p == 1 else \
                None if p == 2 else \
                [] if p == 3 else \
                [2, None] if p == 4 else [2, '']

        g(1)
        self._assertCall(g, 2)
        self._assertCall(g, 3)
        g(4)
        self._assertCall(g)

        @Types(p=int)
        def f(p=None):
            pass

        a(1)
        a()
        self._assertCall(a, '')

        @Types(p=Types.NotNone(int))
        def g(p=None):
            pass

        g(1)
        self._assertCall(b)
        self._assertCall(b, '')

        @Types(p=[int])
        def h(p=None):
            pass

        h([1])
        h([2, 3])
        h([None])
        h([])
        h()
        self._assertCall(h, [2, ''])

        @Types(p=[Types.NotNone(int)])
        def i(p=None):
            pass

        i([1])
        i([2, 3])
        self._assertCall(i, [None])
        i([])
        i()
        self._assertCall(i, [2, ''])

        @Types(p=Types.NotEmpty([int]))
        def d(p=None):
            pass

        d()
        d([1])
        d([2, 3])
        self._assertCall(d, 3)
        self._assertCall(d, [])
        self._assertCall(d, [2, ''])

    def testInterceptor(self):

        def interception(target, args, kwargs):
            raise Exception()

        @Interceptor(interception)
        def a(a, b=2):
            pass

        self._assertCall(a, a=None)
        self._assertCall(a)

    def testCurried(self):

        @Curried()
        def a(b, c=None):
            pass

        result = a()

        self.assertTrue(isinstance(result, Curried.CurriedResult))

        self.assertTrue(a(None) is None)

        result.decorator.args = []

        self.assertTrue(a(b=None) is None)

        self.assertTrue(a(b=None, c=None) is None)

        self.assertTrue(isinstance(a(None), Curried.CurriedResult))

        pass

    def testRetries(self):

        global count
        count = 10

        @Retries(10, delay=0, backoff=0)
        def a():
            global count
            count -= 1
            if count > 0:
                raise Exception()
            else:
                return ""

        result = a()

        self.assertTrue(count == 0)
        self.assertTrue(result == "")

if __name__ == '__main__':
    unittest.main()
