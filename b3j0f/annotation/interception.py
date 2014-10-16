# -*- coding: utf-8 -*-

"""
Definition of annotation dedicated to intercept annotated element calls.
"""
from b3j0f.annotation.core import Annotation
from b3j0f.aop.advice import weave, unweave

__all__ = [
    'Interceptor',
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

    INTERCEPTS = 'intercepts'

    _PRE_INTERCEPTION = '_pre_intercepts'
    _POST_INTERCEPTION = '_post_intercepts'
    _INTERCEPTION = '_interception'

    _ENABLE = '_enable'

    __slots__ = (
        INTERCEPTS,
        _PRE_INTERCEPTION,
        _POST_INTERCEPTION,
        _INTERCEPTION) + Annotation.__slots__

    def __init__(
        self,
        interception=None, pre_interception=None, post_interception=None,
        enable=True,
        *args, **kwargs
    ):
        """
        Default constructor with (pre/post) interception callable objects.

        interception and pre_interception must contains two parameters such as the interceptor and an interceptionContext.
        post_interception must be parameterized by an interceptor, an interceptionContext and interception result.
        """

        super(Interceptor, self).__init__(*args, **kwargs)

        self.interception = interception
        self.pre_interception = pre_interception
        self.post_interception = post_interception
        self.enable = enable

    def __delete__(self):
        """
        Unweave self among self target
        """

        super(Interceptor, self).__delete__(self)

        unweave(self.target, advices=self.intercepts)

    def _bind_target(self, target):
        """
        Weave self.intercepts among target advices
        """

        weave(target, advices=self.intercepts)

    def intercepts(self, advicesexecutor):
        """
        Self target interception
        """

        if self._enable:

            if self.pre_interception is not None:
                self.pre_interception(
                    self,
                    args=advicesexecutor.args,
                    kwargs=advicesexecutor.kwargs)

            if self.interception is not None:
                result = self.interception(self, advicesexecutor)

            if self.post_interception is not None:
                self.post_interception(self, result=result)

    def enable(self, enable=None):
        """
        Get self enable interception state.
        If enable is not None (True or False), change self enable.
        """

        result = self._enable if enable is None else enable

        if enable is not None:

            self._enable = enable

        return result

    @staticmethod
    def enable_interceptors(target, enable=True):
        """
        (Dis|En)able annotated interceptors.
        """

        interceptors = Interceptor.get_annotations(target)

        for interceptor in interceptors:
            interceptor.enable(enable)
