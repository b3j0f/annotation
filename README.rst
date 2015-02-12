b3j0f.annotation: Python annotation library
===========================================

This library aims to provides tools to do annotation in a reflective language.

.. image:: https://pypip.in/license/b3j0f.annotation/badge.svg
   :target: https://pypi.python.org/pypi/b3j0f.annotation/
   :alt: License

.. image:: https://pypip.in/status/b3j0f.annotation/badge.svg
   :target: https://pypi.python.org/pypi/b3j0f.annotation/
   :alt: Development Status

.. image:: https://pypip.in/version/b3j0f.annotation/badge.svg?text=version
   :target: https://pypi.python.org/pypi/b3j0f.annotation/
   :alt: Latest release

.. image:: https://pypip.in/py_versions/b3j0f.annotation/badge.svg
   :target: https://pypi.python.org/pypi/b3j0f.annotation/
   :alt: Supported Python versions

.. image:: https://pypip.in/implementation/b3j0f.annotation/badge.svg
   :target: https://pypi.python.org/pypi/b3j0f.annotation/
   :alt: Supported Python implementations

.. image:: https://pypip.in/format/b3j0f.annotation/badge.svg
   :target: https://pypi.python.org/pypi/b3j0f.annotation/
   :alt: Download format

.. image:: https://travis-ci.org/b3j0f/annotation.svg?branch=master
   :target: https://travis-ci.org/b3j0f/annotation
   :alt: Build status

.. image:: https://coveralls.io/repos/b3j0f/annotation/badge.png
   :target: https://coveralls.io/r/b3j0f/annotation
   :alt: Code test coverage

.. image:: https://pypip.in/download/b3j0f.annotation/badge.svg?period=month
   :target: https://pypi.python.org/pypi/b3j0f.annotation/
   :alt: Downloads

Links
-----

- `Homepage`_
- `PyPI`_
- `Documentation`_

Installation
------------

pip install b3j0f.annotation

Features
--------

What does mean annotations in a reflective way:

- one annotation can annotate several objects at a time (modules, classes, functions, instances, builtins, annotation like themselves, etc.).
- such as a reflective object, they could have their own behavior and lifecycle independently to annotated elements.

This library provides the base Annotation class in order to specialize your own annotations, and several examples of useful annotation given in different modules such as:

- async: dedicated to asynchronous programming.
- interception: annotations able to intercept callable object calls.
- call: inherits from interception module and provides annotations which allow to do checking on callable objects.
- check: annotations which check some conditions such as type of annotated targets, max number of annotated elements, etc.
- oop: useful in object oriented programming like allowing to weave mixins.

Examples
--------

Perspectives
------------

- Cython implementation.

Changelog
---------

0.1.2 (02/12/2015)
##################

- Move code from the package annotation to the module core.

Donating
--------

.. image:: https://cdn.rawgit.com/gratipay/gratipay-badge/2.3.0/dist/gratipay.png
   :target: https://gratipay.com/b3j0f/
   :alt: I'm grateful for gifts, but don't have a specific funding goal.

.. _Homepage: https://github.com/b3j0f/annotation
.. _Documentation: http://pythonhosted.org/b3j0f.annotation
.. _PyPI: https://pypi.python.org/pypi/b3j0f.annotation/
