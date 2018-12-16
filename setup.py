#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re

from setuptools import setup


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


def get_long_description():
    """
    Return the README.
    """
    return open('README.md', 'r', encoding="utf8").read()


def get_packages(package):
    """
    Return root package and all sub-packages.
    """
    return [dirpath
            for dirpath, dirnames, filenames in os.walk(package)
            if os.path.exists(os.path.join(dirpath, '__init__.py'))]


setup(
    name='asgi-chat',
    version=get_version('asgi-chat'),
    url='https://github.com/aitbrahim/asgi-chat',
    description='Broadcast layer for starlete WS',
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    author='Mostafa Aitbrahim',
    author_email='aitbrahim.mostapha@gmail.com',
    packages=get_packages('asgi-chat'),
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Learners',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
