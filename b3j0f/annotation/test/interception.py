#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import main

from b3j0f.utils.ut import UTCase
from b3j0f.annotation.interception import Interceptor, CallInterceptor


class InterceptorTest(UTCase):
    """
    Base class for other tests
    """

    def setUp(self):

        self.count = 0

        self.interceptor = Interceptor(
            interception=self.interception,
            pointcut='__call__')

        self.interceptor(self)

    def interception(self, interceptor, advicesexecutor):

        self.count += 1

        return advicesexecutor.execute()

    def tearDown(self):
        """
        Delete self.interceptor
        """

        del self.interceptor

    def __call__(self):
        """
        Simulate a call for intercepts itself with annotation
        """

        pass


class InterceptionTest(InterceptorTest):
    """
    Test interception
    """

    def test_one_one(self):
        """
        Test one annotation and one call
        """

        self()

        self.assertEqual(self.count, 1)

    def test_one_two(self):
        """
        Test one annotation and two calls
        """
        self()
        self()

        self.assertEqual(self.count, 2)

    def test_two_one(self):
        """
        Test two annotation and one call
        """

        self.interceptor(self)

        self()

        self.assertEqual(self.count, 2)

    def test_two_two(self):
        """
        Test two annotations and two calls
        """

        self.interceptor(self)

        self()
        self()

        self.assertEqual(self.count, 4)


class EnableTest(InterceptorTest):
    """
    Test enable
    """

    def test_enable(self):

        self.interceptor = True

        self()

        self.assertEqual(self.count, 1)

    def test_disable(self):

        self.interceptor = False

        self()

        self.assertEqual(self.count, 0)

    def test_enables(self):

        Interceptor.enable(self, enable=True)

        self()

        self.assertEqual(self.count, 1)

    def test_disables(self):

        Interceptor.enable(self, enable=False)

        self()

        self.assertEqual(self.count, 0)


class CallInterceptorTest(InterceptorTest):
    """
    Test CallInterceptor
    """

    def setUp(self):

        super(CallInterceptorTest, self).setUp()

        del self.interceptor

        self.interceptor = CallInterceptor(interception=self.interception)

        self.interceptor(self)

    def test(self):
        """
        Test interception of self
        """

        self()

        self.assertEqual(self.count, 1)


if __name__ == '__main__':
    main()
