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
Annotations dedicated to object oriented programming.
"""

from b3j0f.annotation import Annotation
from b3j0f.annotation.interception import Interceptor, PrivateInterceptor

from types import MethodType

from inspect import getmembers, isfunction, ismethod, isclass

from warnings import warn_explicit


class MixIn(Annotation):
    """Annotation which enrichs a target with MixIn.

    For every defined mixin, a private couple of (name, array of mixed items)
    is created into the target in order to go back in a no mixin state.
    """

    class MixInError(Exception):
        """
        Raised for any MixIn error.
        """

        pass

    #: key to organize a dictionary of mixed elements by name in targets.
    __MIXEDIN_KEY__ = '__MIXEDIN__'

    #: Key to identify if a mixin add or replace a content.
    __NEW_CONTENT_KEY__ = '__NEW_CONTENT__'

    def __init__(self, classes=tuple(), *attributes, **named_attributes):

        super(MixIn, self).__init__()

        self.classes = classes if isinstance(classes, tuple) else (classes,)
        self.attributes = attributes
        self.named_attributes = named_attributes

    def on_bind_target(self, target):

        super(MixIn, self).on_bind_target(target)

        for cls in self.classes:
            MixIn.mixin(target, cls)

        for attribute in self.attributes:
            MixIn.mixin(target, attribute)

        for name, attribute in self.named_attributes.iteritems():
            MixIn.mixin(target, attribute, name)

    @staticmethod
    def mixin_class(target, cls):
        """Mix cls content in target.
        """

        for name, field in getmembers(cls):
            MixIn.mixin(target, field, name)

    @staticmethod
    def mixin_function_or_method(
        target, fm, name=None, bound_method=False
    ):
        """Mixin a function or a method into the target.

        If name is not given, then the fm name is used.
        If bound method is True (False by default), the mixin result is a bound
        method to target.
        """

        function = None

        if isfunction(fm):
            function = fm
        elif ismethod(fm):
            function = fm.__func__
        else:
            raise MixIn.MixInError(
                "{0} must be a function or a method.".format(fm))

        if name is None:
            name = fm.__name__

        if not isclass(target) or bound_method:
            _type = type(target)
            _type = Interceptor.get_source_target(_type)
            result = MethodType(function, target, _type)
        else:
            result = MethodType(function, None, target)

        MixIn.set_mixin(target, result, name)

        return result

    @staticmethod
    def mixin(target, resource, name=None):
        """Do the correct mixin depending on the type of input resource.

        - Method or Function: mixin_function_or_method.
        - class: mixin_class.
        - other: set_mixin.

        And returns the result of the choosen method (one or a list of mixins).
        """

        result = None

        if ismethod(resource) or isfunction(resource):
            result = MixIn.mixin_function_or_method(target, resource, name)
        elif isclass(resource):
            result = list()
            for name, content in getmembers(resource):
                if isclass(content):
                    mixin = MixIn.set_mixin(target, content, name)
                else:
                    mixin = MixIn.mixin(target, content, name)
                result.append(mixin)
        else:
            result = MixIn.set_mixin(target, resource, name)

        return result

    @staticmethod
    def get_mixedins_by_name(target):
        """Get a set of couple (name, field) of target mixedin.
        """

        result = getattr(target, MixIn.__MIXEDIN_KEY__, None)

        if result is None:
            result = dict()
            setattr(target, MixIn.__MIXEDIN_KEY__, result)

        return result

    @staticmethod
    def set_mixin(target, resource, name=None, override=True):
        """Set a resource and returns the mixed one in target content or
        MixIn.__NEW_CONTENT_KEY__ if resource name didn't exist in target.

        The optional input property name designates the target content item
        to mix with the resource.
        The override parameter (True by default) permits to replace an old
        resource by the new one.
        """

        if name is None and not hasattr(resource, '__name__'):
            raise MixIn.MixInError(
                "name must be given or resource {0} can't be anonymous"
                .format(resource))

        result = None

        name = resource.__name__ if name is None else name

        mixedins_by_name = MixIn.get_mixedins_by_name(target)

        result = getattr(target, name, MixIn.__NEW_CONTENT_KEY__)

        if override or result == MixIn.__NEW_CONTENT_KEY__:

            if name not in mixedins_by_name:
                mixedins_by_name[name] = (result,)
            else:
                mixedins_by_name[name] += (result,)

            try:
                setattr(target, name, resource)
            except Exception:
                if len(mixedins_by_name[name]) == 1:
                    del mixedins_by_name[name]
                    if len(mixedins_by_name) == 0:
                        delattr(target, MixIn.__MIXEDIN_KEY__)
                else:
                    mixedins_by_name[name] = mixedins_by_name[name][:-2]
                result = None
        else:
            result = None

        return result

    @staticmethod
    def remove_mixin(target, name, mixedin=None, set=True):
        """Remove a mixin with name (and reference) from targetand returns the
        replaced one or None.

        The mixedin parameter designates a mixedin value or the last defined
        mixedin if is None (default).
        If set is True (default), the removed mixedin replaces
        the current mixin.
        """

        try:
            result = getattr(target, name)
        except AttributeError:
            raise MixIn.MixInError(
                "No mixin {0} exists in {1}".format(name, target))

        mixedins_by_name = MixIn.get_mixedins_by_name(target)

        mixedins = mixedins_by_name.get(name)
        if mixedins:

            if mixedin is None:
                mixedin = mixedins[-1]
                mixedins = mixedins[:-2]
            else:
                try:
                    index = mixedins.index(mixedin)
                except ValueError:
                    raise MixIn.MixInError(
                        "Mixedin {0} with name {1} does not exist \
                        in target {2}"
                        .format(mixedin, name, target))
                mixedins = mixedins[0:index] + mixedins[index + 1:]

            if len(mixedins) == 0:
                # force to replace/delete the mixin even if set is False
                # in order to stay in a consistent state
                if mixedin != MixIn.__NEW_CONTENT_KEY__:
                    setattr(target, name, mixedin)
                else:
                    delattr(target, name)
                del mixedins_by_name[name]
            else:
                if set:
                    setattr(target, name, mixedin)
                mixedins_by_name[name] = mixedins

        else:
            # shouldn't be raised except if removing has been done
            # manually
            raise MixIn.MixInError(
                "No mixin {0} exists in {1}".format(name, target))

        # clean mixedins if no one exists
        if len(mixedins_by_name) == 0:
            delattr(target, MixIn.__MIXEDIN_KEY__)

        return result

    @staticmethod
    def remove_all_mixins(target, name=None):
        """Tries to get back target in a no mixin consistent state.
        If name is given, then all mixin related to input name may be removed.
        """

        mixedins_by_name = MixIn.get_mixedins_by_name(target).copy()

        for _name, mixedins in mixedins_by_name.iteritems():
            if name is None or name == _name:
                try:
                    while True:
                        MixIn.remove_mixin(target, _name)
                except MixIn.MixInError:
                    pass


class MethodMixIn(Annotation):
    """Apply a mixin on a method.
    """

    def __init__(self, function, *args, **kwargs):

        super(MethodMixIn, self).__init__(*args, **kwargs)

        self.function = function

    def _bind_target(self, target, *args, **kwargs):

        result = super(MethodMixIn, self)._bind_target(target, *args, **kwargs)

        if ismethod(result):
            cls = target.im_class
            name = target.__name__
            MixIn.mixin_function_or_method(cls, self.function, name)

            return target

        else:
            return self.function


class Deprecated(PrivateInterceptor):
    """Decorator which can be used to mark functions as deprecated. It will
    result in a warning being emitted when the function is used.
    """

    def _interception(self, annotation, advicesexecutor):

        target = advicesexecutor.callee
        warn_explicit(
            "Call to deprecated function {0}.".format(target.__name__),
            category=DeprecationWarning,
            filename=target.func_code.co_filename,
            lineno=target.func_code.co_firstlineno + 1
        )
        result = advicesexecutor.execute()
        return result


class Singleton(Annotation):
    """Transforms cls into a singleton.

    Reference to cls, or to any instance is the same reference.
    """

    def __init__(self, *args, **kwargs):
        super(Singleton, self).__init__()
        self.args = args
        self.kwargs = kwargs

    def _bind_target(self, target):

        target = super(Singleton, self)._bind_target(target)

        instance = target(*self.args, **self.kwargs)
        instance.__call__ = lambda x=None: instance
        target.__call__ = lambda x=None: instance

        return instance
