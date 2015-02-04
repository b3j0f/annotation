#!/usr/bin/env python
# -*- coding: utf-8 -*-

# --------------------------------------------------------------------
# The MIT License (MIT)
#
# Copyright (c) 2015 Jonathan Labéjof <jonathan.labejof@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# --------------------------------------------------------------------

from unittest import main

from b3j0f.utils.ut import UTCase
from b3j0f.annotation import Annotation
from b3j0f.annotation.check import Condition, MaxCount, Target


class ConditionTest(UTCase):

    def setUp(self):

        self.condition = Condition()
        self.condition(self._test)

    def _test(self, **kwargs):

        return kwargs.get('a')


class PreConditionTest(ConditionTest):

    def setUp(self):

        super(PreConditionTest, self).setUp()

        self.condition.pre_cond = self.pre_cond

    def pre_cond(self, joinpoint):
        """
        Precondition which fails if kwargs in joinpoint
        """

        if 'a' in joinpoint.kwargs:
            raise Exception()

    def test_success(self):

        self._test()

    def test_failure(self):

        self.assertRaises(Exception, self._test, a=1)


class PostConditionTest(ConditionTest):

    def setUp(self):

        super(PostConditionTest, self).setUp()

        self.condition.post_cond = self.post_cond

    def post_cond(self, joinpoint):
        """
        Post condition which fails if result is True
        """

        if joinpoint.exec_ctx[Condition.RESULT]:
            raise Exception()

    def test_success(self):

        self._test()

    def test_failure(self):

        self.assertRaises(Exception, self._test, a=True)


class ContextCheckerTest(UTCase):
    """
    Test ContextChecker
    """

    pass


class CheckTests(UTCase):

    def test_class(self):

        class Test(object):
            pass

        MaxCount()(Test)
        self.assertRaises(MaxCount.Error, MaxCount().__call__, Test)

    def test_function(self):

        def test():
            pass

        MaxCount()(test)
        self.assertRaises(MaxCount.Error, MaxCount(), test)

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
