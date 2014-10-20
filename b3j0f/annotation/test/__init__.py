#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import main

from time import sleep

from b3j0f.utils.ut import UTCase
from b3j0f.annotation import Annotation, StopPropagation


class DeleteTest(UTCase):
    """
    Test annotation deletion
    """

    def setUp(self):

        self.annotation = Annotation()

    def test_one_annotation(self):
        """
        Test to delete one bound annotation
        """

        self.annotation(self)

        annotations = Annotation.get_annotations(self)

        self.assertEqual(len(annotations), 1)

        self.annotation.__del__()

        annotations = Annotation.get_annotations(self)

        self.assertFalse(annotations)

    def test_two_annotations(self):
        """
        Test to delete one annotation bound twice on the same element
        """

        self.annotation(self)
        self.annotation(self)

        annotations = Annotation.get_annotations(self)

        self.assertEqual(len(annotations), 2)

        self.annotation.__del__()

        annotations = Annotation.get_annotations(self)

        self.assertFalse(annotations)

    def test_two_annotations_wit_two_objects(self):
        """
        Test to delete one annotations bound to two elements
        """

        self.annotation(self)
        self.annotation(DeleteTest)

        annotations = Annotation.get_annotations(self)

        self.assertEqual(len(annotations), 2)

        annotations = Annotation.get_annotations(DeleteTest)

        self.assertEqual(len(annotations), 1)

        self.annotation.__del__()

        annotations = Annotation.get_annotations(self)

        self.assertFalse(annotations)

        annotations = Annotation.get_annotations(DeleteTest)

        self.assertFalse(annotations)


class RemoveTest(UTCase):
    """
    Test remove class method.
    """

    def setUp(self):

        self.annotation = Annotation()

        class TestAnnotation(Annotation):
            pass

        self.TestAnnotation = TestAnnotation

        self.test_annotation = TestAnnotation()

        self.annotation(self)
        self.test_annotation(self)

    def tearDown(self):

        del self.annotation
        del self.test_annotation

    def test(self):
        """
        Test simple remove
        """

        Annotation.remove(self)

        annotations = Annotation.get_annotations(self)

        self.assertFalse(annotations)

    def test_inheritance(self):

        self.TestAnnotation.remove(self)

        annotations = Annotation.get_annotations(self)

        self.assertEqual(annotations[0], self.annotation)

    def test_exclude(self):

        Annotation.remove(self, exclude=self.TestAnnotation)

        annotations = Annotation.get_annotations(self)

        self.assertEqual(annotations[0], self.test_annotation)


class OnBindTargetTest(UTCase):
    """
    Test on_bind_target handler
    """

    def setUp(self):

        self.count = 0
        self.annotation = Annotation(on_bind_target=self.on_bind_target)

    def tearDown(self):

        del self.annotation

    def on_bind_target(self, annotation, target):
        self.count += 1

    def test_one(self):

        self.annotation(self)

        self.assertEqual(self.count, 1)

    def test_many(self):

        self.annotation(self)
        self.annotation(self)

        self.assertEqual(self.count, 2)

    def test_many_elts(self):

        self.annotation(self)
        self.annotation(OnBindTargetTest)
        self.annotation(OnBindTargetTest)

        self.assertEqual(self.count, 3)


class TargetsTest(UTCase):
    """
    Test targets attribute
    """

    def setUp(self):

        self.annotation = Annotation()

    def tearDown(self):

        del self.annotation

    def test_none(self):

        self.assertFalse(self.annotation.targets)

    def test_one(self):

        self.annotation(self)

        self.assertIn(self, self.annotation.targets)

    def test_many(self):

        self.annotation(self)
        self.annotation(self)

        self.assertIn(self, self.annotation.targets)

    def test_many_many(self):

        self.annotation(self)
        self.annotation(TargetsTest)

        self.assertIn(self, self.annotation.targets)
        self.assertIn(TargetsTest, self.annotation.targets)


class LifeTimeTest(UTCase):
    """
    Test lifetime
    """

    def setUp(self):
        self.lifetime = 0.1

    def test_def(self):
        """
        Test lifetime at definition
        """

        Annotation(lifetime=self.lifetime)(self)

        annotations = Annotation.get_annotations(self)

        self.assertTrue(annotations)

        sleep(2 * self.lifetime)

        annotations = Annotation.get_annotations(self)

        self.assertFalse(annotations)

    def test_run(self):
        """
        Test to set lifetime at runtime
        """

        annotation = Annotation()
        annotation(self)

        annotations = Annotation.get_annotations(self)

        self.assertTrue(annotations)

        annotation.lifetime = self.lifetime

        sleep(2 * self.lifetime)

        annotations = Annotation.get_annotations(self)

        self.assertFalse(annotations)

    def test_run_run(self):
        """
        Test to change lifetime after changing it a first time
        """

        annotation = Annotation()
        annotation(self)

        annotations = Annotation.get_annotations(self)

        self.assertTrue(annotations)

        annotation.lifetime = 5

        self.assertLess(annotation.lifetime, 5)

        annotation.lifetime = 10

        self.assertGreater(annotation.lifetime, 5)

        annotation.lifetime = None

        self.assertIsNone(annotation.lifetime)

        del annotation


class GetAnnotationsTest(UTCase):
    """
    Test to annotate elements
    """

    def setUp(self):

        self.annotation = Annotation()

    def tearDown(self):

        del self.annotation

    def test_None(self):
        """
        Test to annotate None
        """

        self.annotation(None)

        annotations = Annotation.get_annotations(None)

        self.assertTrue(annotations)

    def test_number(self):
        """
        Test to annotate a number
        """

        self.annotation(1)

        annotations = Annotation.get_annotations(1)

        self.assertTrue(annotations)

    def test_function(self):
        """
        Test to annotate a function
        """

        def test():
            pass

        self.annotation(test)

        annotations = Annotation.get_annotations(test)

        self.assertTrue(annotations)

    def test_builtin(self):
        """
        Test to annotate a builtin element
        """

        self.annotation(range)

        annotations = Annotation.get_annotations(range)

        self.assertTrue(annotations)

    def test_class(self):
        """
        Test to annotate a class
        """

        class Test(object):
            pass

        self.annotation(Test)

        annotations = Annotation.get_annotations(Test)

        self.assertTrue(annotations)

    def test_namespace(self):
        """
        Test to annotate a namespace
        """

        class Test:
            pass

        self.annotation(Test)

        annotations = Annotation.get_annotations(Test)

        self.assertTrue(annotations)

    def test_method(self):
        """
        Test to annotate a method
        """

        class Test:
            def test(self):
                pass

        self.annotation(Test.test)

        annotations = Annotation.get_annotations(Test.test)

        self.assertTrue(annotations)

    def test_boundmethod(self):
        """
        Test to annotate a bound method
        """

        class Test:
            def test(self):
                pass

        test = Test()

        self.annotation(test.test)

        annotations = Annotation.get_annotations(test.test)

        self.assertTrue(annotations)

    def test_instance(self):
        """
        Test to annotate an instance
        """

        class Test:
                pass

        test = Test()

        self.annotation(test)

        annotations = Annotation.get_annotations(test)

        self.assertTrue(annotations)

    def test_module(self):
        """
        Test to annotate a module
        """

        import sys

        self.annotation(sys)

        annotations = Annotation.get_annotations(sys)

        self.assertTrue(annotations)


def GetParameterizedAnnotationsTest(UTCase):

    def setUp(self):

        self.annotation = Annotation()

        class BaseTest:
            pass

        class Test(BaseTest):
            pass

        self.annotation(BaseTest)
        self.annotation(Test)

        self.Test = Test
        self.BaseTest = BaseTest

        annotations = Annotation.get_annotations(BaseTest)

        self.assertEqual(len(annotations), 1)

        annotations = Annotation.get_annotations(Test)

        self.assertEqual(len(annotations), 2)

    def test_override(self):
        """
        Test to override annotation
        """

        annotations = Annotation.get_annotations(self.Test)

        self.assertEqual(len(annotations), 2)

        self.annotation.override = True

        annotations = Annotation.get_annotations(self.Test)

        self.assertEqual(len(annotations), 1)

    def test_propagate(self):
        """
        Test to propagate annotation
        """

        self.annotation.propagate = False

        annotations = Annotation.get_annotations(self.Test)

        self.assertEqual(len(annotations), 1)

    def test_exclude(self):
        """
        Test to exclude annotations
        """

        class TestAnnotation(Annotation):
            pass

        test_annotation = TestAnnotation()

        test_annotation(self.Test)
        test_annotation(self.BaseTest)

        annotations = Annotation.get_annotations(self.Test)

        self.assertEqual(len(annotations), 4)

        annotations = Annotation.get_annotations(
            self.Test, exclude=TestAnnotation)

        self.assertEqual(len(annotations), 2)

    def test_stop_propagation(self):
        """
        Test Stop propagation annotation
        """

        stop_propagation = StopPropagation(Annotation)

        stop_propagation(self.BaseTest)

        annotations = Annotation.get_annotations(self.Test)

        self.assertEqual(len(annotations), 1)

        stop_propagation.__del__()

        annotations = Annotation.get_annotations(self.Test)

        self.assertEqual(len(annotations), 2)

        stop_propagation(self.Test)

        annotations = Annotation.get_annotations(self.Test)

        self.assertEqual(len(annotations), 0)


class GetAnnotatedFields(UTCase):
    """
    Test get_annotated_fields class method
    """

    def test(self):

        annotation = Annotation()

        field_names = dir(self)

        fields = set()

        for field_name in list(field_names):

            field = getattr(self, field_name)

            try:
                annotation(field)
            except TypeError:
                continue
            fields.add(field)

        annotated_fields = Annotation.get_annotated_fields(self)

        self.assertEqual(len(annotated_fields), len(fields))

        for annotated_field in annotated_fields:

            annotations = annotated_fields[annotated_field]

            self.assertIs(annotations[0], annotation)


if __name__ == '__main__':
    main()
