# -*- coding: utf-8 -*-

"""
Contains base concepts for all other PyCoAnn library objects.
"""

from b3j0f.utils.property import (
    get_properties, put_properties, del_properties, get_local_property,
    get_property
)


class Annotation(object):
    """
    Base class for the python library decorator.
    Contains functions to override in order to catch initialisation
    of this decorator and annotated elements binding
    (also called commonly target in the context of Annotation).

    All annotations which inherit from this are registered to target objects
    and are accessibles through the static method Annotation.get_annotations.

    Instance methods to override are:
    - __init__: set parameters during its instantiation.
    - bind_target: called to bind target to this.
    - on_bind_target: fired when the annotated element is bound to this.

    It is also possible to set an on bind target handler in constructor.
    """

    #: attribute name for accessing to annotated element annotations
    __ANNOTATIONS_KEY__ = '__ANNOTATIONS__'

    #: attribute name for accessing to annotated element from an annotation
    __TARGET_KEY__ = '__TARGET__'

    #: attribute name for target binding notifying
    _ON_BIND_TARGET = 'on_bind_target'

    #: attribute name for annotation inheritance scope.
    _INHERITANCE_SCOPE = 'inheritance_scope'

    #: attribute name for overriding base annotations.
    _OVERRIDE = 'override'

    __slots__ = (
        __ANNOTATIONS_KEY__,
        __TARGET_KEY__,
        _ON_BIND_TARGET,
        _INHERITANCE_SCOPE,
        _OVERRIDE)

    #: dictionary of not modifiable targets
    __NOT_MODIFIABLE_TARGETS__ = {}

    def __init__(
        self, on_bind_target=None, inheritance_scope=False, override=None
    ):
        """
        Default constructor with an 'on_bind_target' handler and inheritance
        scope property.

        :param on_bind_target: function to call when the annotation is bound to
            an object.
        :param bool inheritance_scope: ensure annotation inheritance if target
            is a class or an object.
        :param type overriding: override base annotations with the same types
        """

        super(Annotation, self).__init__()

        self.on_bind_target = on_bind_target
        self.inheritance = inheritance_scope
        self.override = override

    def __call__(self, target):
        """
        Shouldn't be overriden by sub classes.
        """

        # bind target to self
        result = self.bind_target(target)

        return result

    def bind_target(self, target):
        """
        Bind self annotation to target.

        :param target: target to annotate
        :return: bound target
        """

        # process self _bind_target
        result = self._bind_target(target)

        # fire on bind target event
        if self._on_bind_target is not None:
            self._on_bind_target(target)

        return result

    def _bind_target(self, target):
        """
        Method to override in order to specialize binding of target

        :param target: target to bind
        :return: bound target
        """

        result = self.target = target

        # get annotations from target if exists.
        annotations = Annotation.get_local_annotations(target)
        annotations = list(annotations)

        # append self to list of annotation.
        annotations.append(self)

        # set target to self
        put_properties(self, **{Annotation.__TARGET_KEY__: target})

        # annotate target with annotations
        Annotation.set_annotations(target=target, *annotations)

        return result

    def __delete__(self):
        """
        Remove self to self.target annotations
        """

        # get target annotations
        annotations = Annotation.get_local_annotations(self.target)
        # remove self from annotations
        annotations = tuple((
            annotation for annotation in annotations if annotation is not self
        ))
        # update annotations in target
        Annotation.set_annotations(self.target, annotations)

    @staticmethod
    def get_local_annotations(target):
        """
        Get a list of local target annotations in the order of their
            definition.

        :return: target local annotations
        """

        result = get_local_property(target, Annotation.__ANNOTATIONS_KEY__, [])

        return result

    @staticmethod
    def set_annotations(target, *annotations):
        """
        Set input annotations to input target. Old annotaitons will be removed.

        :param target: target to annotate
        :param annotations: annotations to bind to input target
        """

        put_properties(target, Annotation.__ANNOTATIONS_KEY__, annotations)

    @classmethod
    def get_annotations(
        annotation_type, target, inherited=True, forbidden_types=tuple()
    ):
        """
        Returns all input target annotations of annotation_type type ordered by
        definition order.
        Two optional input filters can be parameterized.
        'inherited' check for annotations which inherit from annotation_type.
        'forbidden_types' annotation types to remove from selection.
        """

        result = []

        annotations_key = Annotation.__ANNOTATIONS_KEY__

        property_elts = get_properties(target, annotations_key)

        for elt in property_elts:

            annotations = property_elts[annotations_key]

            for annotation in annotations:

                if isinstance(annotation, forbidden_types) or \
                        (inherited
                            and not isinstance(annotation, annotation_type)):
                    continue

                else:
                    result.append(annotation)

        return result

    @classmethod
    def get_annotated_fields(annotation_type, instance):
        """
        Get arrays of (annotated fields, annotations) by annotation_type of \
        input instance.
        """

        result = {}

        field_names = dir(instance)

        for field_name in field_names:
            field = getattr(instance, field_name)
            annotations = annotation_type.get_annotations(field)

            if annotations:
                result[field] = annotations

        return result


class InheritanceScope(Annotation):
    """
    Set inherit property on annotation.
    """

    def on_bind_target(self, target):

        super(InheritanceScope, self).on_bind_target(target)
        # set inheritance scope to true on annotation target type
        annotated_target = Annotation.get_annotated_target(target)
        setattr(annotated_target, Annotation._INHERITANCE_SCOPE, True)


class StopInheritance(Annotation):
    """
    Stop Inheritance for annotation types.
    """

    def __init__(self, *annotation_types):
        """
        Define annotation types to forbid at this level.
        """

        self.annotation_types = annotation_types
