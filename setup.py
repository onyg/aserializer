#!/usr/bin/env python
 # -*- coding: utf-8 -*-

import sys
from setuptools import setup, find_packages
try:
    import multiprocessing
except ImportError:
    pass



CLASSIFIERS = [
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
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
    author='Ronald Martins',
    author_email='developer@onyg.de',
    license='MIT',
    description='Object serializer inspired by the django forms.',
    url='https://github.com/onyg/aserializer',
    packages= find_packages(exclude=('tests', 'tests.*')),
    platforms=['any'],
    classifiers=CLASSIFIERS,
    test_suite='nose.collector',
    **extra_opts
)
setup(**basic_setup)
