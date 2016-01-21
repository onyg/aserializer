# -*- coding: utf-8 -*-
import os
import unittest
try:
    import django
except ImportError:
    django = None


if django is not None:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.django_tests.django_app.settings')
    from django.test import TestCase
    from django.test.runner import DiscoverRunner
    from django.test.utils import setup_test_environment
    if django.VERSION >= (1, 7, 0):
        django.setup()
else:
    from unittest import TestCase

SKIPTEST_TEXT = "Django is not installed."
SKIPTEST_TEXT_VERSION_18 = "Django >= 1.8 is not installed."
DJANGO_RUNNER = None
DJANGO_RUNNER_STATE = None


def setUpModule():
    if django is None:
        raise unittest.SkipTest(SKIPTEST_TEXT)
    setup_test_environment()
    global DJANGO_RUNNER
    global DJANGO_RUNNER_STATE
    DJANGO_RUNNER = DiscoverRunner()
    DJANGO_RUNNER_STATE = DJANGO_RUNNER.setup_databases()


def tearDownModule():
    if django is None:
        return
    global DJANGO_RUNNER
    global DJANGO_RUNNER_STATE
    if DJANGO_RUNNER and DJANGO_RUNNER_STATE:
        DJANGO_RUNNER.teardown_databases(DJANGO_RUNNER_STATE)