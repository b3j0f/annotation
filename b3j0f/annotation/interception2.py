# -*- coding: utf-8 -*-

"""
Definition of annotation dedicated to intercept annotated element calls.
"""
from b3j0f.annotation.core import Annotation
from functools import wraps
from inspect import isclass, isfunction, ismethod

__all__ = [
    'Interceptor',
    'InterceptorWithoutParameters',
    'NewInterceptor',
    'NewInterceptorWithoutParameters'
    ]


class Interceptor(Annotation):
    """
    Annotation which provides methods in order to intercept annotated elements\
    calls through a wrapper creation.

    A wrapper replaces the definition of the annotated element in the\
    current python runtime. Therefore an interceptor is bound to it through
    the instance method Annotation.get_target().

    A wrapper has the same name and module than the wrapped element.
    In the case of a class wrapper, the wrapped element is in wrapper bases.
    It is possible to identify a wrapper with the static method \
    Interceptor.is_wrapper(wrapper).

    In a chain of interceptors, it is possible to get the source annotated \
    element in using the method Interceptor.get_source_wrapped(wrapper).

    Finally, interception are enabled (default) or not with the instance
    method Interceptor.enabled(enable=True).

    By recursivity, this interceptor can be a wrapper, therefore the instance \
    method Interceptor._super(interceptor_instance) should be used instead of \
    the built-in method super(interceptor_instance, type) in order to use \
    the static method Interceptor.get_source_wrapped(wrapper) instead of the \
    wrapper.

    Methods to override are:
    - _pre_intercepts(self, target, args, kwargs) called before the \
    interception.
    - _intercepts(self, target, args, kwargs) called at interception.
    - _post_intercepts(self, target, result, args, kwargs) called after the \
    interception.
    """

    # static key which bound a wrapper to its wrapped element.
    _WRAPPED = '_wrapped'

    # static key which check if this interceptor is enabled or not.
    _ENABLED = '_enabled'

    __PRE_INTERCEPTION_KEY__ = '__PRE_INTERCEPTION__'
    __INTERCEPTION_KEY__ = '__INTERCEPTION__'
    __POST_INTERCEPTION_KEY__ = '__POST_INTERCEPTION__'

    def __init__(
        self, interception=None, pre_interception=None, post_interception=None,
        on_bind_target=None, inheritance_scope=False, overriding=False
    ):
        """
        Default constructor with (pre/post) interception functions.
        """

        super(Interceptor, self).__init__(
            on_bind_target=on_bind_target,
            inheritance_scope=inheritance_scope,
            overriding=overriding)

        setattr(self, Interceptor.__PRE_INTERCEPTION_KEY__, pre_interception)
        setattr(self, Interceptor.__INTERCEPTION_KEY__, interception)
        setattr(self, Interceptor.__POST_INTERCEPTION_KEY__, post_interception)

    def _get_function_wrapper(self, target):
        """
        Function wrapper.
        """

        @wraps(target)
        def functionWrapper(*args, **kwargs):
            """
            Wraps target if related interception is enabled.
            """

            interceptors = Interceptor.get_annotations(target)

            Interceptor.InterceptionContext()

            result = self.intercepts(target, args, kwargs)

            return result

        result = functionWrapper

        return result

    def _get__call__wrapper(self, target):
        """
        __call__ method class wrapper.
        """

        result = None

        __call__ = getattr(target, '__call__', None)

        if __call__ is not None:
            result = self._get_function_wrapper(__call__)

        return result

    def _bind_target(self, target):
        """
        Get a wrapper related to input target element.
        """

        target = self._super(Interceptor)._bind_target(target)

        # get wrapper specific to target
        if isclass(target):
            __init__ = getattr(target, '__init__', None)
            if __init__ is not None:
                result = self._get_function_wrapper(__init__)
                setattr(target, '__init__', __init__)
            result = target
        elif isfunction(target):
            result = self._get_function_wrapper(target)
        elif ismethod(target):
            result = self._get_function_wrapper(target)
        elif isinstance(target, Interceptor):
            target = Interceptor.get_wrapper(target)
            result = self._get_wrapper(target)
            return result
        else:
            raise Exception('Element {0} can not be annotated by {1}'.format(
                target, self))

        # update self, target and wrapper.
        self._update(target, wrapper=result)

        return result

    def _update(self, target, wrapper):
        """
        Update self, target and wrapper attributes.
        """

        # get annotations from target if exists.
        annotations = getattr(target, Annotation.__ANNOTATIONS_KEY__, [])

        # update annotations to wrapper.
        setattr(wrapper, Annotation.__ANNOTATIONS_KEY__, annotations)

        # set wrapper in all annotations.
        for annotation in annotations:
            setattr(annotation, Annotation.__TARGET_KEY__, wrapper)

        # save target in wrapper.
        setattr(wrapper, Interceptor._WRAPPED, target)

    def _pre_intercepts(self, target, args, kwargs):
        """
        Method to override in order to specialize target pre interception.
        By default, do nothing.
        """

        if self.get_pre_interception() is not None:
            self.pre_interception(self, target, args, kwargs)

    def get_pre_interception(self):

        result = getattr(self, Interceptor.__PRE_INTERCEPTION_KEY__, None)

        return result

    def _intercepts(self, target, args, kwargs):
        """
        Method to override in order to specialize target interception.
        By default, call target with input args and kwargs parameters.
        """

        interception = self.get_interception()
        if interception is not None:
            result = interception(self, target, args, kwargs)
        else:
            result = target(*args, **kwargs)

        return result

    def get_interception(self):

        result = getattr(self, Interceptor.__INTERCEPTION_KEY__, None)

        return result

    def _post_intercepts(self, target, args, kwargs, result):
        """
        Method to override in order to specialize post interception.
        By default, do nothing.
        """

        if self.get_post_interception() is not None:
            self.post_interception(self, target, args, kwargs, result)

    def get_post_interception(self):

        result = getattr(self, Interceptor.__POST_INTERCEPTION_KEY__, None)

        return result

    def intercepts(self, target, args, kwargs):
        """
        Interception method on target with args and kwargs.
        """

        if getattr(self, Interceptor._ENABLED, True):
            # pre-call wrapper
            self._pre_intercepts(target, args, kwargs)
            # call wrapper
            result = self._intercepts(target, args, kwargs)
            # post-call wrapper
            self._post_intercepts(target, args, kwargs, result)
        else:
            result = target(*args, **kwargs)

        return result

    def enable(self, enable=True):
        """
        (Dis|En)able this interception.
        """

        setattr(self, Interceptor._ENABLED, enable)

    @staticmethod
    def get_wrapped(target):
        """
        Return input target wrapped or target if target is not a wrapper
        """

        result = getattr(target, Interceptor._WRAPPED, target)

        return result

    @staticmethod
    def get_source_wrapped(wrapper):
        """
        Get wrapper's source target or wrapper if wrapper is not a wrapper.
        """

        result = wrapper

        while Interceptor.is_wrapper(result):
            result = Interceptor.get_wrapped(result)

        return result

    @staticmethod
    def is_wrapper(target):
        """
        True iif input target is a wrapper.
        """

        result = hasattr(target, Interceptor._WRAPPED)

        return result

    @staticmethod
    def get_annotated_target(target):
        """
        Allow in some specific case to find the right
        annotated element which is not always the target.
        It is useful in order to compare with the get_target method.
        """

        result = Interceptor.get_source_wrapped(target) \
            if Interceptor.is_wrapper(target) \
            else Annotation.get_annotated_target(target)

        return result

    @staticmethod
    def enable_interceptors(target, enable=True):
        """
        (Dis|En)able target interceptors.
        """

        source_target = Interceptor.get_source_wrapped(target)
        interceptors = Interceptor.get_annotations(source_target)

        for interceptor in interceptors:
            interceptor.enable(enable)

from b3j0f.annotation.core import AnnotationWithoutParameters


class InterceptorWithoutParameters(AnnotationWithoutParameters, Interceptor):
    """
    Interception which could be called without parenthesis.
    """
    def __init__(self):
        InterceptorWithoutParameters.__init__(self)
        Interceptor.__init__(self)

    pass


class NewInterceptor(Interceptor):
    """
    Interceptor which generates a class wrapper which inherits from
    Interceptor.
    """

    def _get_class_wrapper(self, target):
        """
        Get a Class wrapper which inherits from both target and Interceptor.
        """

        __dict__ = self._get_wrapper_dict(target)

        target_name = getattr(target, '__name__')

        bases = self._get_wrapper_bases(target)

        result = type(target_name, bases, __dict__)

        return result

    def _get_wrapper_bases(self, target):
        """
        Bases classes for new Interceptor to generate.
        """

        result = (target, Interceptor)

        return result

    def _get_wrapper_dict(self, target):

        result = dict()
        result['__module__'] = target.__module__
        result['__doc__'] = target.__doc__

        return result


class NewInterceptorWithoutParameters(
    InterceptorWithoutParameters, NewInterceptor
):
    """
    Interceptor which transforms a class into an InterceptorWithoutParameters
    without using inheritance.
    """

    def __init__(self):
        InterceptorWithoutParameters.__init__(self)
        NewInterceptor.__init__(self)

    def _get_wrapper_bases(self, target):

        result = (target, InterceptorWithoutParameters)

        return result
