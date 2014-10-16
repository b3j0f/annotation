#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import inspect
from b3j0f.annotation.core \
    import Annotation, AnnotationWithoutParameters, StopInheritance


class TestAnnotation(Annotation):

    def __init__(self, a):

        super(TestAnnotation, self).__init__()

        self.a = a

    def on_bind_target(self, target):
        self.b = 2 * self.a


class TestAnnotationWithoutParameters(AnnotationWithoutParameters):

    def on_bind_target(self, target):
        self.a = 1


class CoreTests(unittest.TestCase):

    def setUp(self):
        self.Annotations_count = 2

    def _testAnnotationsOnTarget(self, target, annotations_count):

        annotations = Annotation.get_annotations(target)

        self.assertEquals(len(annotations), annotations_count)

        for i in range(annotations_count):
            annotation = annotations[i]
            _target = Annotation.get_annotated_target(target)
            self.assertEquals(annotation.get_target(), _target)
            self.assertEquals(annotation.b, 2 * i)
            if isinstance(annotation, TestAnnotation):
                self.assertEquals(annotation.a, i)

        annotations = Annotation.get_annotations(target, inherited=False)

        self.assertEquals(len(annotations), self.Annotations_count)

    def update_annotation(self, a):
        def on_bind_target(annotation, target):
            annotation.b = a * 2
        return on_bind_target

    def testAnnotationOnFunc(self):

        @TestAnnotation(3)
        @TestAnnotation(2)
        @Annotation(on_bind_target=self.update_annotation(1))
        @Annotation(on_bind_target=self.update_annotation(0))
        def a():
            pass

        self._testAnnotationsOnTarget(a, 4)

        TestAnnotation(4)(a)

        self._testAnnotationsOnTarget(a, 5)

    def testAnnotationOnClass(self):
        @TestAnnotation(3)
        @TestAnnotation(2)
        @Annotation(on_bind_target=self.update_annotation(1))
        @Annotation(on_bind_target=self.update_annotation(0))
        class a():
            pass

        self._testAnnotationsOnTarget(a, 4)

        TestAnnotation(4)(a)

        self._testAnnotationsOnTarget(a, 5)

    def testAnnotationOnMethod(self):
        class A(object):

            @TestAnnotation(3)
            @TestAnnotation(2)
            @Annotation(on_bind_target=self.update_annotation(1))
            @Annotation(on_bind_target=self.update_annotation(0))
            def b(self):
                pass

        self._testAnnotationsOnTarget(A.b, 4)

        TestAnnotation(4)(A.b)

        self._testAnnotationsOnTarget(A.b, 5)

    def _testInheritance(self, subsubtarget, subtarget, target, final_target):

        # check base target with two annotations
        subsubannotations = Annotation.get_annotations(subsubtarget)
        self.assertEquals(len(subsubannotations), 2)

        # check mid target with inheritance of one annotation
        subannotations = Annotation.get_annotations(subtarget)
        self.assertEquals(len(subannotations), 1)

        # check target with one stop annotation on all annotations
        # and one annotation
        annotations = Annotation.get_annotations(target)
        self.assertEquals(len(annotations), 2)

        # check final_target with one overriden annotation on all annotations
        # and one annotation
        final_annotations = Annotation.get_annotations(final_target)
        self.assertEquals(len(final_annotations), 1)

    def testClassInheritance(self):

        @Annotation(inheritance_scope=True)
        @Annotation()
        class A(object):
            pass

        class B(A):
            pass

        @Annotation()
        @StopInheritance(Annotation)
        class C(B):
            pass

        @Annotation(overriding=True)
        class D(C):
            pass

        self._testInheritance(A, B, C, D)

    def testMethodInheritance(self):

        class A(object):

            @Annotation(inheritance_scope=True)
            @Annotation()
            def a(self):
                pass

        class B(A):
            pass

        class C(B):

            @Annotation()
            @StopInheritance(Annotation)
            def a(self):
                pass

        class D(C):

            @Annotation(overriding=True)
            def a(self):
                pass

        self._testInheritance(A.a, B.a, C.a, D.a)

    def _testAnnotationWithoutParameters(self, target):

        annotations = Annotation.get_annotations(target)
        self.assertEquals(len(annotations), 2)
        for annotation in annotations:
            if inspect.ismethod(target):
                self.assertEquals(annotation.get_target(), target.im_func)
            else:
                self.assertEquals(annotation.get_target(), target)
            self.assertTrue(hasattr(annotation, 'a'))

    def testAnnotationWithoutParametersOnFunction(self):

        @TestAnnotationWithoutParameters
        @TestAnnotationWithoutParameters()
        def a():
            pass

        self._testAnnotationWithoutParameters(a)

    def testAnnotationWithoutParametersOnClass(self):

        @TestAnnotationWithoutParameters
        @TestAnnotationWithoutParameters()
        class A(object):
            pass

        self._testAnnotationWithoutParameters(A)

    def testAnnotationWithoutParametersOnMethod(self):

        class A(object):
            @TestAnnotationWithoutParameters
            @TestAnnotationWithoutParameters()
            def a(self):
                pass

        self._testAnnotationWithoutParameters(A.a)

if __name__ == '__main__':
    unittest.main()
