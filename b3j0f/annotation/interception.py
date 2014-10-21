# -*- coding: utf-8 -*-

"""
Definition of annotation dedicated to intercept annotated element calls.
"""
from b3j0f.annotation import Annotation
from b3j0f.aop.advice import weave, unweave

__all__ = ('Interceptor')


class Interceptor(Annotation):
    """
    Annotation able to intercept annotated elements.

    This interception can be disabled at any time and specialized with a
        pointcut.
    """

    #: attribute name for doing the interception
    INTERCEPTION = 'interception'

    #: attribute name for pointcut
    POINTCUT = 'pointcut'

    #: attribure name for enable the interception
    ENABLE = 'enable'

    #: private attribute name for pointcut
    _POINTCUT = '_pointcut'

    __slots__ = (
        INTERCEPTION, ENABLE,  # public attributes
        _POINTCUT  # private attribute
    ) + Annotation.__slots__

    class InterceptorError(Exception):
        """
        Handle Interceptor errors
        """

        pass

    def __init__(
        self, interception=None, pointcut=None, enable=True, *args, **kwargs
    ):
        """
        Default constructor with interception function and enable property.

        :param callable interception: called if self is enabled and if any
            annotated element is called. Parameters of call are self annotation
            and an AdvicesExecutor.
        :param pointcut: pointcut to use in order to weave interception.
        :param bool enable:
        """

        super(Interceptor, self).__init__(*args, **kwargs)

        setattr(self, Interceptor.INTERCEPTION, interception)
        setattr(self, Interceptor._POINTCUT, pointcut)
        setattr(self, Interceptor.ENABLE, enable)

    def __del__(self):
        """
        Unweave self from self targets
        """

        try:
            super(Interceptor, self).__delete__(self)

            pointcut = getattr(self, Interceptor.POINTCUT)

            for target in self.targets:

                unweave(target, pointcut=pointcut, advices=self.intercepts)

        except AttributeError:
            # raised if self is already deleted
            pass

    @property
    def pointcut(self):
        return self._pointcut

    @pointcut.setter
    def pointcut(self, value):
        """
        Change of pointcut
        """

        pointcut = getattr(self, Interceptor.POINTCUT)

        # for all targets
        for target in self.targets:
            # unweave old advices
            unweave(target, pointcut=pointcut, advices=self.intercepts)
            # weave new advices with new pointcut
            weave(target, pointcut=value, advices=self.intercepts)

        # and save new pointcut
        setattr(self, Interceptor._POINTCUT, value)

    def _bind_target(self, target, *args, **kwargs):
        """
        Weave self.intercepts among target advices with pointcut
        """

        super(Interceptor, self)._bind_target(target=target, *args, **kwargs)

        pointcut = getattr(self, Interceptor.POINTCUT)
        weave(target, pointcut=pointcut, advices=self.intercepts)

    def intercepts(self, advicesexecutor):
        """
        Self target interception if self is enabled

        :param advicesexecutor: advices executor
        """

        if self.enable:

            interception = getattr(self, Interceptor.INTERCEPTION)
            try:
                interception(self, advicesexecutor)
            except Exception as e:
                raise Interceptor.InterceptorError(e)

    @classmethod
    def set_enable(interceptor_type, target, enable=True):
        """
        (Dis|En)able annotated interceptors.
        """

        interceptors = interceptor_type.get_annotations(target)

        for interceptor in interceptors:
            setattr(interceptor, Interceptor.ENABLE, enable)


class CallInterceptor(Interceptor):
    """
    Interceptor dedicated to intercept call of annotated element.

    Instead of Interceptor, the pointcut equals '__call__'.

    It could be used to intercepts annotation binding annotated by self.
    """

    __CALL__ = '__call__'

    __slots__ = Interceptor.__slots__

    def __init__(self, *args, **kwargs):

        super(CallInterceptor, self).__init__(
            pointcut=CallInterceptor.__CALL__, *args, **kwargs)
