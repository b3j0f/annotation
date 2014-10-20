# -*- coding: utf-8 -*-

"""
Decorators dedicated to class or functions calls.
"""

from b3j0f.annotation.interception import Interceptor

try:
    from inspect import getcallargs
except ImportError:
    from inspect import getargspec, ismethod
    from sys import getdefaultencoding

    def getcallargs(func, *positional, **named):
        """Get the mapping of arguments to values.

        A dict is returned, with keys the function argument names (including the
        names of the * and ** arguments, if any), and values the respective bound
        values from 'positional' and 'named'."""
        args, varargs, varkw, defaults = getargspec(func)
        f_name = func.__name__
        arg2value = {}

        # The following closures are basically because of tuple parameter unpacking.
        assigned_tuple_params = []

        def assign(arg, value):
            if isinstance(arg, str):
                arg2value[arg] = value
            else:
                assigned_tuple_params.append(arg)
                value = iter(value)
                for i, subarg in enumerate(arg):
                    try:
                        subvalue = next(value)
                    except StopIteration:
                        raise ValueError('need more than %d %s to unpack' %
                                         (i, 'values' if i > 1 else 'value'))
                    assign(subarg, subvalue)
                try:
                    next(value)
                except StopIteration:
                    pass
                else:
                    raise ValueError('too many values to unpack')

        def is_assigned(arg):
            if isinstance(arg, str):
                return arg in arg2value
            return arg in assigned_tuple_params

        if ismethod(func) and func.im_self is not None:
            # implicit 'self' (or 'cls' for classmethods) argument
            positional = (func.im_self,) + positional
        num_pos = len(positional)
        num_total = num_pos + len(named)
        num_args = len(args)
        num_defaults = len(defaults) if defaults else 0
        for arg, value in zip(args, positional):
            assign(arg, value)
        if varargs:
            if num_pos > num_args:
                assign(varargs, positional[-(num_pos - num_args):])
            else:
                assign(varargs, ())
        elif 0 < num_args < num_pos:
            raise TypeError('%s() takes %s %d %s (%d given)' % (
                f_name, 'at most' if defaults else 'exactly', num_args,
                'arguments' if num_args > 1 else 'argument', num_total))
        elif num_args == 0 and num_total:
            if varkw:
                if num_pos:
                    # XXX: We should use num_pos, but Python also uses num_total:
                    raise TypeError('%s() takes exactly 0 arguments '
                                    '(%d given)' % (f_name, num_total))
            else:
                raise TypeError('%s() takes no arguments (%d given)' %
                                (f_name, num_total))
        for arg in args:
            if isinstance(arg, str) and arg in named:
                if is_assigned(arg):
                    raise TypeError("%s() got multiple values for keyword "
                                    "argument '%s'" % (f_name, arg))
                else:
                    assign(arg, named.pop(arg))
        if defaults:    # fill in any missing values with the defaults
            for arg, value in zip(args[-num_defaults:], defaults):
                if not is_assigned(arg):
                    assign(arg, value)
        if varkw:
            assign(varkw, named)
        elif named:
            unexpected = next(iter(named))
            if isinstance(unexpected, unicode):
                unexpected = unexpected.encode(getdefaultencoding(), 'replace')
            raise TypeError("%s() got an unexpected keyword argument '%s'" %
                            (f_name, unexpected))
        unassigned = num_args - len([arg for arg in args if is_assigned(arg)])
        if unassigned:
            num_required = num_args - num_defaults
            raise TypeError('%s() takes %s %d %s (%d given)' % (
                f_name, 'at least' if defaults else 'exactly', num_required,
                'arguments' if num_required > 1 else 'argument', num_total))
        return arg2value

from sys import stderr

from time import sleep


class Types(Interceptor):

    class TypesError(Exception):
        pass

    class _SpecialCondition(object):

        def __init__(self, _type):

            self._type = _type

        def get_type(self):

            return self._type

    class NotNone(_SpecialCondition):
        pass

    class NotEmpty(_SpecialCondition):
        pass

    class _NamedParameterType(object):

        def __init__(self, name, parameter_type):

            self._name = name
            self._parameter_type = parameter_type

    class _NamedParameterTypes(object):

        def __init__(self, target, named_parameter_types):

            self._named_parameter_types = []

            for index in range(target.__code__.co_argcount):
                target_parameter_name = target.__code__.co_varnames[index]

                if target_parameter_name in named_parameter_types:
                    parameter_type = \
                        named_parameter_types[target_parameter_name]
                    named_parameter_type = \
                        Types._NamedParameterType(
                            target_parameter_name,
                            parameter_type)
                    self._named_parameter_types.append(named_parameter_type)

                else:
                    self._named_parameter_types.append(None)

    """
    Check parameter or result types of decorated class or function call.
    """
    def __init__(self, result_type=None, **named_parameter_types):

        self._super(Types).__init__()
        self.result_type = result_type
        self.named_parameter_types = named_parameter_types

    @staticmethod
    def check_value(value, expected_type):

        result = False

        if isinstance(expected_type, Types.NotNone):
            result = value is not None and Types.check_value(
                value,
                expected_type.get_type())

        else:
            result = value is None

            if not result:

                value_type = type(value)

                if isinstance(expected_type, Types.NotEmpty):
                    try:
                        result = len(value) != 0
                        if result:
                            _type = expected_type.get_type()
                            result = Types.check_value(value, _type)
                    except TypeError:
                        result = False

                elif isinstance(expected_type, list):
                    result = issubclass(value_type, list)

                    if result:
                        if len(expected_type) == 0:
                            result = len(value) == 0
                        else:
                            _expected_type = expected_type[0]

                            for item in value:
                                result = Types.check_value(
                                    item,
                                    _expected_type)

                                if not result:
                                    break

                elif isinstance(expected_type, set):
                    result = issubclass(value_type, set)

                    if result:
                        if len(expected_type) == 0:
                            result = len(value) == 0
                        else:

                            _expected_type = expected_type.copy().pop()
                            _value = value.copy()

                            value_length = len(_value)

                            for count in range(value_length):
                                item = _value.pop()
                                result = Types.check_value(
                                    item,
                                    _expected_type)

                                if not result:
                                    break
                else:
                    result = issubclass(value_type, expected_type)

        return result

    def _pre_intercepts(self, target, args, kwargs):

        if self.named_parameter_types:
            callargs = getcallargs(target, *args, **kwargs)

            for arg in callargs:
                value = callargs[arg]
                expected_type = self.named_parameter_types.get(arg)

                if expected_type is not None and \
                    not Types.check_value(
                        value,
                        expected_type):
                    raise Types.TypesError(
                        "wrong typed parameter for arg {0} : {1} ({2}). \
                        Expected: {3}.".format(
                        (arg, value, type(value), expected_type)))

    def _post_intercepts(self, target, args, kwargs, result):

        if self.result_type:
            if not Types.check_value(result, self.result_type):
                raise Types.TypesError(
                    "wrong result type for {0} with parameters {1}, {2}: {3} \
                    ({4}). Expected {5}.".
                    format(
                        target, args, kwargs, result, type(result),
                        self.result_type))


class Curried(Interceptor):
    """
    Inspirated from Jeff Laughlin Consulting LLC projects.

    Decorator that returns a function that keeps returning functions
    until all arguments are supplied; then the original function is
    evaluated.
    """

    class CurriedResult(object):
        """
        Curried result in case of missing arguments.
        """

        def __init__(self, decorator, exception):

            self.decorator = decorator
            self.exception = exception

    def __init__(self, *args, **kwargs):

        self._super(Curried).__init__()
        self.args = self.default_args = args
        self.kwargs = self.default_kwargs = kwargs

    def _intercepts(self, target, args, kwargs):

        result = None

        self.kwargs.update(kwargs)
        self.args += args

        try:
            # check if all arguments are given
            getcallargs(target, *self.args, **self.kwargs)
        except TypeError as te:
            # in case of problem, returns curried decorater and exception
            result = Curried.CurriedResult(self, te)

        if result is None:
            # call target with all arguments
            result = target(*self.args, **self.kwargs)

        return result


def example_exc_handler(tries_remaining, exception, delay):
    """Example exception handler; prints a warning to stderr.

    tries_remaining: The number of tries remaining.
    exception: The exception instance which was raised.
    """

    print >> stderr, "Caught '{0}', {1} tries remaining, \
    sleeping for {2} seconds".format(exception, tries_remaining, delay)


class Retries(Interceptor):
    """Function decorator implementing retrying logic.

    delay: Sleep this many seconds * backoff * try number after failure
    backoff: Multiply delay by this factor after each failure
    exceptions: A tuple of exception classes; default (Exception,)
    hook: A function with the signature myhook(tries_remaining, exception);
          default None

    The decorator will call the function up to max_tries times if it raises
    an exception.

    By default it catches instances of the Exception class and subclasses.
    This will recover after all but the most fatal errors. You may specify a
    custom tuple of exception classes with the 'exceptions' argument; the
    function will only be retried if it raises one of the specified
    exceptions.

    Additionally you may specify a hook function which will be called prior
    to retrying with the number of remaining tries and the exception instance;
    see given example. This is primarily intended to give the opportunity to
    log the failure. Hook is not called after failure if no retries remain.
    """

    def __init__(
        self,
        max_tries,
        delay=1,
        backoff=2,
        exceptions=(Exception,),
        hook=None
    ):

        self._super(Retries).__init__()
        self.max_tries = max_tries
        self.delay = delay
        self.backoff = backoff
        self.exceptions = exceptions
        self.hook = hook

    def _intercepts(self, target, args, kwargs):

        mydelay = self.delay
        tries = range(self.max_tries)
        tries.reverse()

        for tries_remaining in tries:

            try:
                return target(*args, **kwargs)

            except self.exceptions as e:

                if tries_remaining > 0:

                    if self.hook is not None:
                        self.hook(tries_remaining, e, mydelay)

                    sleep(mydelay)
                    mydelay = mydelay * self.backoff

                else:
                    raise
            else:
                break
