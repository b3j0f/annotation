#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from b3j0f.annotation.oop import MixIn, MethodMixIn, Deprecated, Singleton


class OOPTests(unittest.TestCase):

    def setUp(self):
        pass

    def testMixIn(self):

        class A(object):
            def plop(self):
                pass

        plop = A.plop

        mixedins_by_name = MixIn.get_mixedins_by_name(A)

        self.assertEqual(len(mixedins_by_name), 0)

        MixIn.set_mixin(A, 2, 'a')
        MixIn.set_mixin(A, lambda: None, 'b')
        MixIn.set_mixin(A, None, 'plop')
        MixIn.set_mixin(A, None, 'plop')
        MixIn.set_mixin(A, None, 'plop')

        mixedins_by_name = MixIn.get_mixedins_by_name(A)

        self.assertEqual(len(mixedins_by_name), 3)
        self.assertEqual(A.a, 2)
        self.assertEqual(A.plop, None)

        MixIn.remove_mixin(A, 'plop')

        mixedins_by_name = MixIn.get_mixedins_by_name(A)

        self.assertEqual(len(mixedins_by_name), 3)

        MixIn.remove_all_mixins(A)

        mixedins_by_name = MixIn.get_mixedins_by_name(A)

        self.assertEqual(len(mixedins_by_name), 0)
        self.assertFalse(hasattr(A, 'a'))
        self.assertTrue(plop == A.plop)

    def testClassMixIn(self):

        class ClassForMixIn(object):
            def get_1(self):
                return 1

            def get_2(self):
                return 2

        def get_3(self):
            return self.a

        a = None

        @MixIn(ClassForMixIn, lambda: None, get_3=get_3, a=a)
        class MixedInClass(object):
            def get_1(self):
                return '1'

            def get_3(self):
                return 3

        self.assertTrue(hasattr(MixedInClass, 'get_2'))
        self.assertTrue(hasattr(MixedInClass, 'a'))
        self.assertTrue(hasattr(MixedInClass, '<lambda>'))

        mixedInstance = MixedInClass()

        self.assertEqual(mixedInstance.a, None)
        self.assertTrue(mixedInstance.get_3() == a)
        self.assertTrue(mixedInstance.get_1() is 1)

        MixIn.remove_all_mixins(MixedInClass)
        self.assertTrue(mixedInstance.get_3() == 3)
        self.assertTrue(mixedInstance.get_1() is '1')

        MixIn(ClassForMixIn, lambda: None, get_3=get_3, a=a)(MixedInClass)

        self.assertTrue(hasattr(MixedInClass, 'get_2'))
        self.assertTrue(hasattr(MixedInClass, 'a'))
        self.assertTrue(hasattr(MixedInClass, '<lambda>'))

        self.assertEqual(mixedInstance.a, None)
        self.assertTrue(mixedInstance.get_3() == a)
        self.assertTrue(mixedInstance.get_1() is 1)

    def testMethodMixIn(self):

        def plop(self):
            return None

        class MixedInClass(object):

            @MethodMixIn(plop)
            def get_1(self):
                return 1

        self.assertTrue(hasattr(MixedInClass, 'get_1'))

        mixedInstance = MixedInClass()

        self.assertEqual(mixedInstance.get_1(), None)

        class MixedInClass(object):

            def get_1(self):
                return 1

        MethodMixIn(plop)(MixedInClass.get_1)

        self.assertTrue(hasattr(MixedInClass, 'get_1'))

        mixedInstance = MixedInClass()

        self.assertEqual(mixedInstance.get_1(), None)

        MixIn.remove_all_mixins(MixedInClass)

        self.assertEqual(mixedInstance.get_1(), 1)

    def testDeprecated(self):

        @Deprecated
        def b():
            pass

        b()

    def testSingleton(self):

        @Singleton(a=1)
        class A(object):
            def __init__(self, a):
                self.a = a

            def get_a(self):
                return self.a

        self.assertEqual(A, A())

        self.assertEqual(A(), A())

        self.assertEqual(A.get_a(), A().get_a())

if __name__ == '__main__':
    unittest.main()
