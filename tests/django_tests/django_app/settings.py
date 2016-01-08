# -*- coding: utf-8 -*-

"""
Settings for aserializer/Django tests.
"""

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
    }
}

SECRET_KEY = 'SECRET_KEY_FOR_TESTING.'

INSTALLED_APPS = [
    'tests.django_tests.django_app',
]

MIDDLEWARE_CLASSES = ()

