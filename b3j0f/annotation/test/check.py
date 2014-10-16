#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from b3j0f.annotation.interception import Interceptor
from b3j0f.annotation.check import Condition, Checker, MaxCount, Target


class CheckTests(unittest.TestCase):

    def setUp(self):
        pass

    def testPreCondition(self):

        def precond(target, args, kwargs):
            kwargs['a'] *= 2

        @Condition(pre=precond)
        def a(a):
            return a

        self.assertTrue(a(a=2) == 4)

    def testPostCondition(self):

        def postcond(target, result, args, kwargs):
            if result == 0:
                raise Exception()

        @Condition(post=postcond)
        def a(a):
            return a

        self._assertCall(a, 0)
        a(1)

    def testChecker(self):

        @Checker(lambda decorator_type, target: type(target) == type)
        class A(object):
            pass

        e = None

        @A()
        class B(object):
            pass

        try:
            @A()
            def c():
                pass
        except Exception as e:
            pass

        self.assertTrue(e is not None)

    def testMaxCount(self):

        e = None

        try:
            @MaxCount(1)
            @MaxCount(1)
            class A(object):
                pass
        except Exception as e:
            pass

        self.assertTrue(e is not None)

        e = None

        @MaxCount(1)
        class Test1(Interceptor):
            pass

        try:
            @Test1()
            @Test1()
            def b():
                pass
        except Exception as e:
            pass

        self.assertTrue(e is not None)

        e = None

        @MaxCount(2)
        class Test2(Interceptor):
            pass

        @Test2()
        @Test2()
        def c():
            pass

        try:
            @Test2()
            @Test2()
            @Test2()
            def d():
                pass
        except Exception as e:
            pass

        self.assertTrue(e is not None)

    def testTarget(self):

        @Target(type)
        class A(Interceptor):
            pass

        e = None

        try:
            @A()
            def a():
                pass
        except Exception as e:
            pass

        self.assertTrue(e is not None)

        e = None

        @A()
        class CA(object):
            pass

        @Target(Target.FUNC)
        class B(Interceptor):
            pass

        @B()
        def b():
            pass

        try:
            @B()
            class CB(object):
                pass
        except Exception as e:
            pass

        self.assertTrue(e is not None)

        e = None

        @Target(CheckTests)
        class C(Interceptor):
            pass

        try:
            @C()
            def c():
                pass
        except Exception as e:
            pass

        self.assertTrue(e is not None)

        e = None

        @C()
        class CC(CheckTests):
            pass

        @Target([MaxCount, Target], rule=Target.AND)
        class D(Interceptor):
            pass

        @D()
        class DD(MaxCount, Target):
            pass

        try:
            @D()
            class DDD(MaxCount):
                pass
        except Exception as e:
            pass

        self.assertTrue(e is not None)

        @Target([MaxCount, str], rule=Target.OR)
        class D(Interceptor):
            pass

        @D()
        class EE(MaxCount):
            pass

        try:
            @D()
            class EEE(object):
                pass
        except Exception as e:
            pass

        self.assertTrue(e is not None)

if __name__ == '__main__':
    unittest.main()
