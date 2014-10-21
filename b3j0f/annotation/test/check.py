#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import main

from b3j0f.utils.ut import UTCase
from b3j0f.annotation import Annotation
from b3j0f.annotation.check import Condition, MaxCount, Target


class ConditionTest(UTCase):

    def setUp(self):

        self.condition = Condition()
        self.condition(self.test)

    def test(self, a=None):

        return a


class PreConditionTest(ConditionTest):

    def setUp(self):

        super(PreConditionTest, self).setUp()

        self.condition.pre_cond = self.pre_cond

    def pre_cond(self, annotation, advicesexecutor):
        """
        Precondition which fails if kwargs in advicesexecutor
        """

        if advicesexecutor.kwargs:
            raise Exception()

    def test_success(self):

        self.test()

    def test_failure(self):

        self.assertRaises(Exception, self.test, a=1)


class PostConditionTest(ConditionTest):

    def setUp(self):

        super(PostConditionTest, self).setUp()

        self.condition.post_cond = self.post_cond

    def post_cond(self, annotation, result, advicesexecutor):
        """
        Post condition which fails if result is True
        """

        if result:
            raise Exception()

    def test_success(self):

        self.test()

    def test_failure(self):

        self.assertRaises(Exception, self.test, a=True)


class CheckTests(UTCase):

    def testMaxCount(self):

        e = None

        try:
            @MaxCount(1)
            @MaxCount(1)
            class A(object):
                pass
        except Exception as e:
            pass

        self.assertIsNotNone(e)

        e = None

        @MaxCount(1)
        class Test1(Annotation):
            pass

        try:
            @Test1()
            @Test1()
            def b():
                pass
        except Exception as e:
            pass

        self.assertIsNotNone(e)

        e = None

        @MaxCount(2)
        class Test2(Annotation):
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

        self.assertIsNotNone(e)

    def testTarget(self):

        @Target(type)
        class A(Annotation):
            pass

        e = None

        try:
            @A()
            def a():
                pass
        except Exception as e:
            pass

        self.assertIsNotNone(e)

        e = None

        @A()
        class CA(object):
            pass

        @Target(Target.FUNC)
        class B(Annotation):
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

        self.assertIsNotNone(e)

        e = None

        @Target(CheckTests)
        class C(Annotation):
            pass

        try:
            @C()
            def c():
                pass
        except Exception as e:
            pass

        self.assertIsNotNone(e)

        e = None

        @C()
        class CC(CheckTests):
            pass

        @Target([MaxCount, Target], rule=Target.AND)
        class D(Annotation):
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

        self.assertIsNotNone(e)

        @Target([MaxCount, str], rule=Target.OR)
        class D(Annotation):
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

        self.assertIsNotNone(e)


if __name__ == '__main__':
    main()
