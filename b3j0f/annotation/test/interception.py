#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from b3j0f.annotation.interception \
    import Interceptor, InterceptorWithoutParameters, NewInterceptor


class InterceptionTests(unittest.TestCase):

    def setUp(self):
        pass

    @Interceptor()
    def testInterceptor(self):

        Interceptors = Interceptor.get_annotations(
            target=InterceptionTests.testInterceptor)
        self.assertEquals(len(Interceptors), 1)

        @Interceptor()
        class SubInterceptor(Interceptor):
            """
            Test Interceptor
            """
            pass

        self.assertTrue(issubclass(SubInterceptor, Interceptor))

        Interceptors = Interceptor.get_annotations(
            target=InterceptionTests.testInterceptor)
        self.assertEquals(len(Interceptors), 1)

        self.assertTrue(isinstance(Interceptors[0], Interceptor))
        self.assertTrue(issubclass(type(Interceptors[0]), Interceptor))

        @SubInterceptor()
        @Interceptor()
        def a():
            pass

        Interceptors = Interceptor.get_annotations(target=a)
        self.assertEquals(len(Interceptors), 2)

        Interceptors = SubInterceptor.get_annotations(target=a)
        self.assertEquals(len(Interceptors), 1)

        Interceptors = Interceptor.get_annotations(
            target=a,
            inherited=False)
        self.assertEquals(len(Interceptors), 1)

        @Interceptor()
        @SubInterceptor()
        class A(object):
            """
            Test Interceptor
            """
            pass

        self.assertTrue(issubclass(A, object))

        Interceptors = Interceptor.get_annotations(target=A)
        self.assertEquals(len(Interceptors), 2)

        Interceptors = SubInterceptor.get_annotations(target=A)
        self.assertEquals(len(Interceptors), 1)

        Interceptors = Interceptor.get_annotations(
            target=A,
            inherited=False)
        self.assertEquals(len(Interceptors), 1)

        """
        To do those tests, Interceptor needs to implement the __new__ method
        instead of the __init__ method.
        The result depends on the target. If target is None,
        the result is the Interceptor instance, else it's the wrapper.
        """
        @Interceptor()
        @Interceptor()
        @SubInterceptor()
        def b():
            pass

        Interceptors = Interceptor.get_annotations(target=b)
        self.assertEquals(len(Interceptors), 3)

        Interceptors = Interceptor.get_annotations(target=b)
        self.assertEquals(len(Interceptors), 3)

        Interceptors = SubInterceptor.get_annotations(target=b)
        self.assertEquals(len(Interceptors), 1)

        Interceptors = Interceptor.get_annotations(
            target=b,
            inherited=False)
        self.assertEquals(len(Interceptors), 2)

    @InterceptorWithoutParameters
    def testInterceptorWithoutParameters(self):

        Interceptors = Interceptor.get_annotations(
            target=InterceptionTests.testInterceptor)
        self.assertEquals(len(Interceptors), 1)

        @InterceptorWithoutParameters
        class SubInterceptor(InterceptorWithoutParameters):
            """
            Test Interceptor
            """

            pass

        self.assertTrue(issubclass(SubInterceptor, Interceptor))

        Interceptors = Interceptor.get_annotations(
            target=InterceptionTests.testInterceptor)
        self.assertEquals(len(Interceptors), 1)

        self.assertTrue(isinstance(Interceptors[0], Interceptor))
        self.assertTrue(issubclass(type(Interceptors[0]), Interceptor))

        @SubInterceptor
        @InterceptorWithoutParameters
        def _a():
            pass

        interceptors = Interceptor.get_annotations(target=_a)
        self.assertEquals(len(interceptors), 2)

        interceptors = SubInterceptor.get_annotations(
            target=_a)
        self.assertEquals(len(interceptors), 1)

        interceptors = InterceptorWithoutParameters.get_annotations(
            target=_a,
            inherited=False)
        self.assertEquals(len(interceptors), 1)

        @InterceptorWithoutParameters
        @SubInterceptor
        class A(object):
            """
            Test Interceptor
            """

            pass

        self.assertTrue(issubclass(A, object))

        Interceptors = Interceptor.get_annotations(target=A)
        self.assertEquals(len(Interceptors), 2)

        Interceptors = SubInterceptor.get_annotations(target=A)
        self.assertEquals(len(Interceptors), 1)

        Interceptors = InterceptorWithoutParameters.get_annotations(
            target=A,
            inherited=False)
        self.assertEquals(len(Interceptors), 1)

        """
        To do those tests, Interceptor needs to implement
        the __new__ method instead of the __init__ method.
        The result depends on the target. If target is None,
        the result is the Interceptor instance, else it's the wrapper.
        """
        @InterceptorWithoutParameters
        @InterceptorWithoutParameters
        @SubInterceptor
        def b():
            pass

        Interceptors = Interceptor.get_annotations(target=b)
        self.assertEquals(len(Interceptors), 3)

        Interceptors = Interceptor.get_annotations(target=b)
        self.assertEquals(len(Interceptors), 3)

        Interceptors = SubInterceptor.get_annotations(target=b)
        self.assertEquals(len(Interceptors), 1)

        Interceptors = InterceptorWithoutParameters.get_annotations(
            target=b,
            inherited=False)
        self.assertEquals(len(Interceptors), 2)

    checked = False

    def assertChecked(self):
        self.assertTrue(InterceptionTests.checked)
        InterceptionTests.checked = False

    def testNewInterceptor(self):

        @NewInterceptor()
        class A(object):
            def _intercepts(self, target, args, kwargs):
                InterceptionTests.checked = True

        @A()
        def g():
            pass

        g()

        self.assertChecked()

        @NewInterceptor()
        class B(object):
            def __init__(self, a, b=None):
                super(Interceptor, self).__init__()

            def on_bind_target(self, target):
                InterceptionTests.checked = True

        e = None

        try:
            @B()
            def i():
                pass
        except Exception as e:
            pass

        self.assertTrue(e is not None)

        @B(a=1)
        def j():
            pass

        self.assertChecked()

        j()

        e = None

        try:
            @B(a=1, c=2)
            def k():
                pass
        except Exception as e:
            pass

        self.assertTrue(e is not None)

    def testInheritance(self):

        class A(Interceptor):
            def __init__(self, a, b=None):
                super(A, self).__init__()

            def _intercepts(self, target, args, kwargs):
                InterceptionTests.checked = True

        e = None

        try:
            @A()
            def a():
                pass
        except Exception as e:
            pass

        self.assertTrue(e is not None)
        e = None

        try:
            @A(b=1)
            def b():
                pass
        except Exception as e:
            pass

        self.assertTrue(e is not None)

        @A(a=None)
        def c():
            pass

        c()

        self.assertChecked()

if __name__ == '__main__':
    unittest.main()
