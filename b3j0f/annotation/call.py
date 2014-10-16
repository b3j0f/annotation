# -*- coding: utf-8 -*-

"""
Decorators dedicated to class or functions calls.
"""

from b3j0f.annotation.interception import Interceptor

import inspect

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
            callargs = inspect.getcallargs(target, *args, **kwargs)

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
            inspect.getcallargs(target, *self.args, **self.kwargs)
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
