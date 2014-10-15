#!/usr/bin/env python
 # -*- coding: utf-8 -*-

import sys
import os
from setuptools import setup, find_packages
try:
    import multiprocessing
except ImportError:
    pass


def get_version():
    with open(os.path.join('aserializer', '__init__.py')) as f:
        for line in f:
            if line.startswith('__version__ ='):
                return line.split('=')[1].strip().strip('"\'')


long_description = (open('README.rst').read())


CLASSIFIERS = [
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Topic :: Software Development :: Libraries :: Python Modules',
]

extra_opts = {}
if "test" in sys.argv or "nosetests" in sys.argv:
    extra_opts['tests_require'] = ['nose', 'coverage']

basic_setup = dict(
    name='aserializer',
    version=get_version(),
    author='Ronald Martins',
    author_email='developer@onyg.de',
    license='MIT',
    description='An object serializer inspired by the django forms.',
    long_description=long_description,
    url='https://github.com/onyg/aserializer',
    packages= find_packages(exclude=('tests', 'tests.*')),
    platforms=['any'],
    classifiers=CLASSIFIERS,
    test_suite='nose.collector',
    **extra_opts
)
setup(**basic_setup)
