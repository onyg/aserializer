# -*- coding: utf-8 -*-

try:
    import django
except ImportError as e:
    django = None
    django_import_error = e


def check_django_import():
    if django is None:
        raise django_import_error


class django_required(object):
    def __call__(self, func):
        def wrapper(self, *args, **kwargs):
            check_django_import()
            return func(self, *args, **kwargs)
        return wrapper
