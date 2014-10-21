"""
Interceptors dedicated to decorate decorations.
"""

from b3j0f.annotation.interception import (
    PrivateInterceptor, PrivateCallInterceptor
)
from b3j0f.utils.property import setdefault, get_local_property, del_properties
from b3j0f.utils.iterable import ensureiterable

from types import FunctionType

__all__ = [
    'Condition', 'ContextChecker', 'MaxCount', 'Target'
]


class Condition(PrivateInterceptor):
    """
    Apply a pre/post condition on an annotated element call.
    """

    #: attribute name for pre condition
    PRE_COND = 'pre_cond'

    #: attribute name for post condition
    POST_COND = 'post_cond'

    __slots__ = (PRE_COND, POST_COND) + PrivateInterceptor.__slots__

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

    def _interception(self, annotation, advicesexecutor):
        """
        Intercept call of advicesexecutor callee in doing pre/post conditions
        """

        if self.pre_cond is not None:
            self.pre_cond(self, advicesexecutor)

        result = advicesexecutor.execute()

        if self.post_cond is not None:
            self.post_cond(self, result, advicesexecutor)

        return result


class ContextChecker(PrivateCallInterceptor):

    __slots__ = PrivateCallInterceptor.__slots__

    __CONTEXT_KEY__ = '__context_checker__'

    def __del__(self):
        """
        Free context memory.
        """

        super(ContextChecker, self).__del__()

        # get context key and self class
        context_key = ContextChecker.__CONTEXT_KEY__
        self_class = self.__class__

        # for all targets
        for target in self.targets:

            # get contexts
            contexts = get_local_property(target, context_key)

            # if not empty
            if self_class in contexts:

                # get context
                context = contexts[self_class]

                # free context if empty
                if not context:
                    del contexts[self_class]

            # if contexts are empty, free them
            if not contexts:
                del_properties(target, context_key)

    def _interception(self, annotation, advicesexecutor):

        # get target, context_key and context
        target = advicesexecutor.callee
        context_key = ContextChecker.__CONTEXT_KEY__
        context = setdefault(target, context_key, {})

        # get self_class and context value
        self_class = self.__class__
        value = context.setdefault(self_class, {})

        # check self on annotation, target and context value
        self._check(annotation, target, value)

        # run the advices executor
        result = advicesexecutor.execute()

        return result

    def _check(self, annotation, target, value):
        """
        Update a context value during annotation binding.

        :param Annotation annotation: annotation in binding to target
        :param target: element during annotation
        :param dict value: value to update
        """

        pass


class MaxCount(ContextChecker):
    """
    Set a maximum count of Interceptor instances per target.
    """

    class MaxCountError(Exception):
        pass

    __COUNT_KEY__ = 'count'

    __slots__ = (__COUNT_KEY__, ) + ContextChecker.__slots__

    def __init__(self, count=1, *args, **kwargs):
        """
        Count of annotation/object call
        """

        super(MaxCount, self).__init__(*args, **kwargs)

        self.count = count

    def _check(self, annotation, target, value, *args, **kwargs):

        super(MaxCount, self)._check(
            annotation, target, value, *args, **kwargs)

        count = value.setdefault(MaxCount.__COUNT_KEY__, self.count - 1)

        if count < 0:
            raise MaxCount.MaxCountError()

# apply MaxCount on itself
MaxCount()(MaxCount)


@MaxCount()
class Target(ContextChecker):
    """
    Check type of all decorated element decorated by this decorated Annotation.
    """

    class TargetError(Exception):
        pass

    __TYPES_ALLOWED_PER_TARGET = {}

    OR = 'or'
    AND = 'and'

    TYPES = 'types'
    RULE = 'rule'

    __slots__ = (TYPES, RULE) + ContextChecker.__slots__

    def __init__(self, types, rule=OR, *args, **kwargs):

        super(Target, self).__init__(*args, **kwargs)

        self.types = ensureiterable(types)
        self.rule = rule

    def _interception(self, annotation, advicesexecutor, *args, **kwargs):

        result = super(Target, self)._interception(
            annotation, advicesexecutor, *args, **kwargs)

        raiseException = self.rule == Target.OR

        target = advicesexecutor.callee

        for _type in self.types:

            if ((_type == type or _type == FunctionType) and isinstance(
                    target, _type)) or issubclass(target, _type):
                if self.rule == Target.OR:
                    raiseException = False
                    break

            elif self.rule == Target.AND:
                raiseException = True
                break

        if raiseException:
            Interceptor_type = type(annotation)

            raise Target.TargetError(
                "{0} is not allowed by {1}. Must be {2} {3}".format(
                    target,
                    Interceptor_type,
                    'among' if self.rule == Target.OR else 'all',
                    self.types))

        return result

    def _check(self, annotation, target, value, *args, **kwargs):

        value[Target.TYPES] = self.types
        value[Target.RULE] = self.rule
