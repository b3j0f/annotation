"""
Interceptors dedicated to decorate decorations.
"""

from b3j0f.annotation.interception import Interceptor, CallInterceptor
from b3j0f.utils.property import setdefault, get_local_property, del_properties

from types import FunctionType


class Condition(Interceptor):
    """
    Apply a pre/post condition on an annotated element call.
    """

    #: attribute name for pre condition
    PRE_CONDITION = 'pre_condition'

    #: attribute name for post condition
    POST_CONDITION = 'post_condition'

    __slots__ = (PRE_CONDITION, POST_CONDITION) + Interceptor.__slots__

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

    def __init__(
        self, pre_condition=None, post_condition=None, *args, **kwargs
    ):
        """
        :param pre_condition: function called before target call. Parameters
            are self annotation and AdvicesExecutor.
        :param post_condition: function called after target call. Parameters
            are self annotation, call result and AdvicesExecutor.
        """

        super(Condition, self).__init__(*args, **kwargs)

        self.pre_condition = pre_condition
        self.post_condition = post_condition

    def interception(self, annotation, advicesexecutor):
        """
        Intercept call of advicesexecutor callee in doing pre/post conditions
        """

        if self.pre_condition is not None:
            self.pre_condition(self, advicesexecutor)

        result = advicesexecutor.execute()

        if self.post_condition is not None:
            self.post_condition(self, result, advicesexecutor)

        return result


class ContextChecker(CallInterceptor):

    __slots__ = CallInterceptor.__slots__

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

    def interception(self, annotation, advicesexecutor):

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

        raise NotImplementedError()


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

    def _check(self, annotation, target, value):

        count = value.setdefault(MaxCount.__COUNT_KEY__, self.count - 1)

        if count < 0:
            raise MaxCount.MaxCountError()


class Target(ContextChecker):
    """
    Check type of all decorated element decorated by this decorated Annotation.
    """

    class TargetError(Exception):
        pass

    __TYPES_ALLOWED_PER_TARGET = {}

    OR = 'or'
    AND = 'and'

    __TYPES__ = 'types'
    __RULE__ = 'rule'

    def __init__(self, types, rule=OR, *args, **kwargs):

        super(Target, self).__init__(*args, **kwargs)

        self.types = types if isinstance(types, list) else [types]
        self.rule = rule

    def interception(self, annotation, target):

        super(Target, self).interception(annotation, target)

        raiseException = self.rule == Target.OR

        for _type in self.types:
            _type = Interceptor.get_source_target(_type)

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
            Interceptor_type = Interceptor.get_source_target(Interceptor_type)

            raise Target.TargetError(
                "{0} is not allowed by {1}. Must be {2} {3}".format(
                    target,
                    Interceptor_type,
                    'among' if self.rule == Target.OR else 'all',
                    self.types))

        return True

    def _check(self, interceptor, target):

        result = {Target.__TYPES__: self.types, Target.__RULE__: self.rule}

        return result
