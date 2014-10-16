# -*- coding: utf-8 -*-

"""
Decorations dedicated to asynchronous programming.
"""

try:
    from threading import Thread, RLock
except ImportError as IE:
    from dummythreading import Thread, RLock

from Queue import Queue

from signal import signal, SIGALRM, alarm

from b3j0f.annotation.interception import Interceptor
from b3j0f.annotation.core import Annotation
from b3j0f.annotation.oop import MixIn


class Synchronized(Interceptor):
    """
    Transform a target into a thread safe target.
    """

    def __init__(self, lock=None):

        self._super(Synchronized, self).__init__()
        self._lock = lock if lock is not None else RLock()

    def _pre_intercepts(self, target, args, kwargs):

        self._super(Synchronized)._pre_intercepts(target, args, kwargs)
        self._lock.acquire()

    def _post_intercepts(self, target, args, kwargs, result):

        self._super(Synchronized)._post_intercepts(
            target, args, kwargs, result)
        self._lock.release()


class SynchronizedClass(Synchronized):
    """
    Transform a class into a thread safe class.
    """

    def on_bind_target(self, target):

        self._super(SynchronizedClass)._on_bind_target(target)
        for attribute in target.__dict__:
            if callable(attribute):
                Synchronized(attribute, self.lock)


class Asynchronous(Annotation):
    """
    Transform a target into an asynchronous callable target.
    """

    def threaded(self, *args, **kwargs):

        result = self.__wraps(args, kwargs)
        self.queue.put(result)

    def on_bind_target(self, target):

        # add start function to wrapper
        super(Asynchronous, self).on_bind_target(target)
        setattr(target, 'start', self.start)

    def start(self, *args, **kwargs):

        self.queue = Queue()
        thread = Thread(target=self.threaded, args=args, kwargs=kwargs)
        thread.start()

        return Asynchronous.Result(self.queue, thread)

    class NotYetDoneException(Exception):

        def __init__(self, message):

            self.message = message

    class Result(object):

        def __init__(self, queue, thread):

            self.queue = queue
            self.thread = thread

        def is_done(self):

            return not self.thread.is_alive()

        def get_result(self, wait=-1):

            if not self.is_done():
                if wait >= 0:
                    self.thread.join(wait)
                else:
                    raise Asynchronous.NotYetDoneException(
                        'the call has not yet completed its task')

            if not hasattr(self, 'result'):
                self.result = self.queue.get()

            return self.result


class TimeOut(Interceptor):
    """
    Raise an Exception if the target call has not finished in time.
    """

    class TimeOutError(Exception):
        """
        Exception thrown if time elapsed before the end of the target call.
        """

        """
        Default time out error message.
        """
        DEFAULT_MESSAGE = \
            'Call of {0} with parameters {1} and {2} is timed out'

        def __init__(self, timeout_interceptor, frame):

            super(TimeOut.TimeOutError, self).__init__(
                timeout_interceptor.message.format(
                    timeout_interceptor.target,
                    timeout_interceptor.args,
                    timeout_interceptor.kwargs)
            )

    def __init__(
        self, seconds, error_message=TimeOutError.DEFAULT_MESSAGE
    ):

        self._super(TimeOut).__init__()
        self._seconds = seconds
        self._error_message = error_message

    def _handle_timeout(self, signum, frame):

        raise TimeOut.TimeOutError(self)

    def _intercepts(self, target, args, kwargs):

        self._target = target
        self._args = args
        self._kwargs = kwargs

        signal(SIGALRM, self._handle_timeout)
        alarm(self._seconds)
        try:
            result = self.target(*args, **kwargs)
        finally:
            signal.alarm(0)

        return result

from time import sleep


class Wait(Interceptor):
    """
    Define a time to wait before and after a target call.
    """

    DEFAULT_WAIT = 1

    def __init__(
        self,
        before_seconds=DEFAULT_WAIT,
        after_seconds=DEFAULT_WAIT,
    ):

        self._super(Wait).__init__()
        self._before_seconds = before_seconds
        self._after_seconds = after_seconds

    def _pre_intercepts(self, target, args, kwargs):

        self._super(Wait)._pre_intercepts(target, args, kwargs)
        sleep(self._before_seconds)

    def _post_intercepts(self, target, args, kwargs, result):

        self.super(Wait)._post_intercepts(target, args, kwargs, result)
        sleep(self._after_seconds)


class Observable(Interceptor):
    """
    Imlementation of the observer design pattern.
    It transforms a target into an observable object in adding method
    registerObserver, unregisterObserver and notify_observers.
    Observers listen to pre/post target interception.
    """

    def __init__(self):
        self._super(Observable).__init__()
        self.observers = set()

    def registerObserver(self, observer):
        """
        Register an observer.
        """

        self.observers.add(observer)

    def unregisterObserver(self, observer):
        """
        Unregister an observer.
        """

        self.observers.remove(observer)

    def notify_observers(self, target, args, kwargs, result=None, post=False):
        """
        Notify observers with parameter calls and information about
        pre/post call.
        """

        _observers = tuple(self.observers)

        for observer in _observers:
            observer.notify(target, args, kwargs, result, post)

    def on_bind_target(self, target):
        MixIn.set_mixin(target, self.registerObserver)
        MixIn.set_mixin(target, self.unregisterObserver)
        MixIn.set_mixin(target, self.notify_observers)

    def _pre_intercepts(self, target, args, kwargs):
        self._super(Observable)._pre_intercepts(target, args, kwargs)
        self.notify_observers(target, args, kwargs)

    def _post_intercepts(self, target, args, kwargs, result):
        self._super(Observable)._post_intercepts(target, args, kwargs)
        self.notify_observers(target, args, kwargs, result, post=True)
