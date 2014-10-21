#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

from os.path import abspath, dirname, join

# get setup directory abspath
_path = dirname(abspath(__file__))

# get long description
with open(join(_path, 'README')) as f:
    desc = f.read()

dependencies = ['b3j0f.aop']

setup(
    name="b3j0f.annotation",
    version="0.1.0",
    install_requires=dependencies,
    packages=find_packages(where='.', exclude=['test.*', '*.test.*']),
    author="b3j0f",
    author_email="jlabejof@yahoo.fr",
    description="Python Annotation Library",
    long_description=desc,
    url='https://github.com/mrbozzo/annotation/',
    license='MIT License',
    classifiers=[
        "Development Status :: 1 - Planning",
        "License :: MIT",
        "Natural Language :: French",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Topic :: Communications",
    ],
    test_suite='b3j0f'
)
