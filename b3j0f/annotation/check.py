"""
Interceptors dedicated to decorate decorations.
"""

from b3j0f.annotation.interception import Interceptor
from b3j0f.annotation.interception import NewInterceptor

from types import FunctionType


class Condition(Interceptor):
    """
    Apply a pre/post condition on an annotated element call.
    """

    class ConditionError(Exception):

        def __init__(self, condition, target, **params):
            message = "Error of {0} on {1} with parameters {2}"\
                .format(condition, target, params)
            super(Condition.ConditionError, self).__init__(message)

    def __init__(self, pre=None, post=None):

        self._super(Condition).__init__()
        self.pre = pre
        self.post = post

    def _pre_intercepts(self, target, args, kwargs):

        if self.pre is not None and not self.pre(target, args, kwargs):
            raise Condition.ConditionError(
                self, "pre-condition", target, args=args, kwargs=kwargs)

    def _post_intercepts(self, target, args, kwargs, result):

        if self.post is not None \
                and not self.post(target, result, args, kwargs):
            raise Condition.ConditionError(
                self, "post-condition", target, args=args, kwargs=kwargs,
                result=result)


class Checked(Interceptor):
    """
    Interceptor which is able to call external checkers \
    when this._call is called.
    """

    __CHECKERS_KEY__ = '__checkers__'

    @classmethod
    def enable_checking(cls, enable=None):
        """
        Enable self checking. If enable is not None, \
        change self state of enable_checkers.
        """

        result = False

        if not hasattr(cls, '_enable_checking'):
            cls._enable_checking = True

        if enable is not None:
            cls._enable_checking = enable

        result = cls._enable_checking

        return result

    @classmethod
    def get_checkers(cls):
        """
        Return self checkers set.
        """

        result = getattr(cls, Checked.__CHECKERS_KEY__, set())

        return result

    def _callCheckers(self, target):
        """
        Call all self checkers only if self enable_checkers is True
        """

        self_type = type(self)

        if self_type.enable_checking():
            checkers = self_type.get_checkers()
            for checker in checkers:
                checker.check(self, target)


class Checker(NewInterceptor):
    """
    Check dynamically the definition of all decorated element decorated by \
    this decorated Interceptor with an input function \'checking\'.
    \'Checking\' function takes in parameters the decorated Interceptor\
    instance and the decorated element definition.
    """

    class CheckerError(Exception):
        pass

    __CHECK_TYPE_PER_TARGET = {}

    def __init__(self, checker):

        self._super(Checker).__init__()
        self.checker = checker

    def _bind_target(self, target):
        """
        Add self to wrapper checkers.
        """

        result = self._super(Checker)._bind_target(target)
        result.get_checkers().add(self)

        return result

    def check(self, interceptor, target):
        """
        Call self checker method with input interceptor and target.
        If the checker method returns False, then throw a CheckerError.
        """

        if not self.checker(interceptor, target):
            raise Checker.CheckerError(
                'checking function {0} on {1} does not check {2}'.format(
                    (self.checker, Interceptor, target)))

    def _get_bases(self, target):
        """
        Add Checked to wrapper base classes.
        """

        result = (target, Checked)

        return result

    def _get_dict(self, target):
        """
        Add _callCheckers in wrapper _on_bind_target method.
        """

        def _on_bind_target(self, target):

            _type = type(self)
            self._super(_type)._on_bind_target(target)
            self._callCheckers(target)

            return target

        result = self._super(Checker)._get_dict(target)
        result['_on_bind_target'] = _on_bind_target

        return result


class ContextChecker(Checker):
    """
    Checker which manages a value in the context of a decorated Interceptor,
    a target and self.
    """

    __ENTRY_PER_TARGET_PER_Interceptor_TYPE = {}

    def __init__(self):

        self._super(ContextChecker).__init__(self._check)

    def _check(self, nterceptor, target):

        return True

    def _get_entry(self, interceptor, target):
        """
        Return an entry in the context of self type,
        Interceptor type and target.
        """

        _type = type(self)
        _type = Interceptor.get_source_target(_type)

        interceptor_type = Interceptor.get_source_target(type(interceptor))

        entry_per_target = \
            ContextChecker.__ENTRY_PER_TARGET_PER_Interceptor_TYPE.get(
                interceptor_type, None)

        _target = Interceptor.get_source_target(target)

        if not entry_per_target:
            result = self._get_default_entry(interceptor, target)

            entry_per_target = {_target: result}
            ContextChecker.__ENTRY_PER_TARGET_PER_Interceptor_TYPE[
                interceptor_type] = entry_per_target

        result = entry_per_target.get(_target, None)

        if not result:
            result = self._get_default_entry(interceptor_type, target)
            entry_per_target[_target] = result

        return result

    def _get_default_entry(self, interceptor, target):
        """
        Return context entry point.
        """

        _type = type(self)
        _type = Interceptor.get_source_target(_type)
        default_value = self._get_default_value(interceptor, target)
        result = {_type: default_value}

        return result

    def _get_value(self, interceptor, target):
        """
        Method to use by sub Interceptors in order to get context value.
        """

        entry = self._get_entry(interceptor, target)
        _type = type(self)
        _type = Interceptor.get_source_target(_type)

        result = entry[_type]
        return result

    def _update_value(self, interceptor, target, value):
        """
        Update a value in the context of Interceptor, target and self.
        """

        entry = self._get_entry(interceptor, target)
        _type = type(self)
        _type = Interceptor.get_source_target(_type)

        entry[_type] = value

    def _get_default_value(self, Interceptor, target):
        """
        Method to override by sub Interceptors.
        """

        return None


class MaxCount(ContextChecker):
    """
    Set a maximum count of Interceptor instances per target.
    """

    class MaxCountError(Exception):
        pass

    __MAX_COUNT_KEY__ = 'MAX_COUNT'

    __COUNT_KEY__ = 'COUNT'

    __COUNT_PER_TARGET = {}

    def __init__(self, count=1):

        self._super(MaxCount).__init__()
        self.count = count

    def _check(self, interceptor, target):

        value = self._get_value(interceptor, target)
        count = value[MaxCount.__COUNT_KEY__]

        if count == 0:
            raise MaxCount.MaxCountError(
                "Too many instances of {0} decorate {1}, at most {2} accepted".
                format(
                    (
                        interceptor,
                        target,
                        value[MaxCount.__MAX_COUNT_KEY__])))

        else:
            value[MaxCount.__COUNT_KEY__] = count - 1

        return True

    def _get_default_value(self, interceptor, target):

        result = {
            MaxCount.__COUNT_KEY__: self.count,
            MaxCount.__MAX_COUNT_KEY__: self.count}

        return result

MaxCount = MaxCount(1)(MaxCount)


@MaxCount(1)
class Target(ContextChecker):
    """
    Check type of all decorated element decorated
    by this decorated Interceptor.
    """

    class TargetError(Exception):
        pass

    __TYPES_ALLOWED_PER_TARGET = {}

    OR = 'or'
    AND = 'and'

    __TYPES__ = 'types'
    __RULE__ = 'rule'

    def __init__(self, types, rule=OR):

        self._super(Target).__init__()
        self.types = types if isinstance(types, list) else [types]
        self.rule = rule

    def _check(self, interceptor, target):
        _target = Interceptor.get_source_target(target)

        raiseException = self.rule == Target.OR

        for _type in self.types:
            _type = Interceptor.get_source_target(_type)

            if ((_type == type or _type == FunctionType) and isinstance(
                    _target, _type)) or issubclass(_target, _type):
                if self.rule == Target.OR:
                    raiseException = False
                    break

            elif self.rule == Target.AND:
                raiseException = True
                break

        if raiseException:
            Interceptor_type = type(interceptor)
            Interceptor_type = Interceptor.get_source_target(Interceptor_type)

            raise Target.TargetError(
                "{0} is not allowed by {1}. Must be {2} {3}".format(
                    _target,
                    Interceptor_type,
                    'among' if self.rule == Target.OR else 'all',
                    self.types))

        return True

    def _get_default_value(self, interceptor, target):

        result = {Target.__TYPES__: self.types, Target.__RULE__: self.rule}

        return result
