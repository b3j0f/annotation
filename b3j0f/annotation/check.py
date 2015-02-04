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

"""
Interceptors dedicated to decorate decorations.
"""

from b3j0f.annotation import Annotation
from b3j0f.annotation.interception import (
    PrivateInterceptor, PrivateCallInterceptor
)
from b3j0f.utils.iterable import ensureiterable

from types import FunctionType

__all__ = [
    'Condition', 'MaxCount', 'Target'
]


class Condition(PrivateInterceptor):
    """
    Apply a pre/post condition on an annotated element call.
    """

    class ConditionError(Exception):
        """
        Handle condition errors
        """

        pass

    class PreConditionError(ConditionError):
        """
        Handle pre condition errors
        """

        pass

    class PostConditionError(ConditionError):
        """
        Handle post condition errors
        """

        pass

    #: pre condition attribute name
    PRE_COND = 'pre_cond'

    #: post condition attribute name
    POST_COND = 'post_cond'

    #: result attribute name
    RESULT = 'result'

    __slots__ = (PRE_COND, POST_COND) + PrivateInterceptor.__slots__

    def __init__(self, pre_cond=None, post_cond=None, *args, **kwargs):
        """
        :param pre_cond: function called before target call. Parameters
            are self annotation and AdvicesExecutor.
        :param post_cond: function called after target call. Parameters
            are self annotation, call result and AdvicesExecutor.
        """

        super(Condition, self).__init__(*args, **kwargs)

        self.pre_cond = pre_cond
        self.post_cond = post_cond

    def _interception(self, joinpoint):
        """
        Intercept call of joinpoint callee in doing pre/post conditions
        """

        if self.pre_cond is not None:
            self.pre_cond(joinpoint)

        result = joinpoint.proceed()

        if self.post_cond is not None:
            joinpoint.exec_ctx[Condition.RESULT] = result
            self.post_cond(joinpoint)

        return result


class AnnotationChecker(PrivateInterceptor):
    """
    Annotation dedicated to intercept annotation target binding.
    """
    __slots = PrivateCallInterceptor.__slots__

    #: bind_target pointcut
    __BIND_TARGET__ = 'bind_target'

    def __init__(self, *args, **kwargs):

        super(AnnotationChecker, self).__init__(
            pointcut=AnnotationChecker.__BIND_TARGET__, *args, **kwargs)


class MaxCount(AnnotationChecker):
    """
    Set a maximum count of Interceptor instances per target.
    """

    class Error(Exception):
        pass

    __COUNT_KEY__ = 'count'

    __slots__ = (__COUNT_KEY__, ) + AnnotationChecker.__slots__

    def __init__(self, count=1, *args, **kwargs):
        """
        Count of annotation/object call
        """

        super(MaxCount, self).__init__(*args, **kwargs)

        self.count = count

    def _interception(self, joinpoint):

        target = joinpoint.kwargs['target']
        annotation = joinpoint.kwargs['self']

        annotation_class = annotation.__class__
        annotations = annotation_class.get_annotations(target)

        if len(annotations) >= self.count:
            raise MaxCount.Error(
                '{0} calls of {1} on {2}'.format(
                    self.count + 1, annotation, target))

        result = joinpoint.proceed()

        return result

# apply MaxCount on itself
MaxCount()(MaxCount)


@MaxCount()
class Target(AnnotationChecker):
    """
    Check type of all decorated element decorated by this decorated Annotation.
    """

    class Error(Exception):
        pass

    FUNC = FunctionType

    OR = 'or'
    AND = 'and'

    TYPES = 'types'
    RULE = 'rule'

    __slots__ = (TYPES, RULE) + PrivateCallInterceptor.__slots__

    def __init__(self, types, rule=OR, *args, **kwargs):

        super(Target, self).__init__(*args, **kwargs)

        self.types = ensureiterable(types)
        self.rule = rule

    def _interception(self, joinpoint):

        raiseException = self.rule == Target.OR

        target = joinpoint.kwargs['target']
        annotation = joinpoint.kwargs['self']

        for _type in self.types:

            if (_type in [type, FunctionType] and isinstance(
                    target, _type)) or issubclass(target, _type):
                if self.rule == Target.OR:
                    raiseException = False
                    break

            elif self.rule == Target.AND:
                raiseException = True
                break

        if raiseException:
            Interceptor_type = type(annotation)

            raise Target.Error(
                "{0} is not allowed by {1}. Must be {2} {3}".format(
                    target,
                    Interceptor_type,
                    'among' if self.rule == Target.OR else 'all',
                    self.types))

        result = joinpoint.proceed()

        return result

# ensure AnnotationChecker and MaxCount are dedicated to Annotation
Target(Annotation)(AnnotationChecker)
