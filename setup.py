#!/usr/bin/env python
 # -*- coding: utf-8 -*-

import sys
from setuptools import setup, find_packages
try:
    import multiprocessing
except ImportError:
    pass


LONG_DESCRIPTION = None
try:
    LONG_DESCRIPTION = open('README.rst').read()
except:
    pass

CLASSIFIERS = [
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Framework :: Django',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    #'Programming Language :: Python :: 3',
    #'Programming Language :: Python :: 3.1',
    #'Programming Language :: Python :: 3.2',
    'Programming Language :: Python :: Implementation :: CPython',
    'Topic :: Software Development :: Libraries :: Python Modules',
]

extra_opts = {}
if "test" in sys.argv or "nosetests" in sys.argv:
    extra_opts['tests_require'] = ['nose', 'coverage', 'blinker']#, 'django>=1.4.2',]

basic_setup = dict(
    name='aserializer',
    version='0.5',
    author='onyg',
    author_email='development@orderbird.com',
    license='BSD',
    description='A serializer for rest.',
    url='',
    long_description=LONG_DESCRIPTION,
    packages= find_packages(exclude=('tests', 'tests.*')),
    platforms=['any'],
    classifiers=CLASSIFIERS,
    test_suite='nose.collector',
    **extra_opts
)
setup(**basic_setup)
