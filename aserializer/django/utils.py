# -*- coding: utf-8 -*-

try:
    import django
    django_version = django.VERSION
except ImportError as e:
    django = None
    django_import_error = e
    django_version = (0, 0, 0)

from aserializer.utils import py2to3


def check_django_import():
    if django is None:
        raise django_import_error


class django_required(object):
    def __call__(self, func):
        def wrapper(self, *args, **kwargs):
            check_django_import()
            return func(self, *args, **kwargs)
        return wrapper


def get_related_model_classes():
    if django is None:
        return ()
    if django_version >= (1, 8, 0):
        from django.db.models import ManyToManyRel, OneToOneRel, ManyToOneRel
        return ManyToManyRel, OneToOneRel, ManyToOneRel
    else:
        from django.db.models.related import RelatedObject
        return RelatedObject


def get_fields(model):
    if django_version >= (1, 8, 0):
        return model._meta.get_fields()
    else:
        fields = [item[0] for item in model._meta.get_fields_with_model()]
        m2m_fields = [item[0] for item in model._meta.get_m2m_with_model()]
        related_m2m_fields = [item[0].field for item in model._meta.get_all_related_m2m_objects_with_model()]
        return fields + m2m_fields + related_m2m_fields


def get_none_realtion_fields(model):
    if django_version < (1, 8, 0):
        return []
    return []


def get_related_fields(model):
    if django_version < (1, 8, 0):
        return []
    return []


def get_relations_fields(model):
    if django_version < (1, 8, 0):
        return []
    return []


def is_relation_field(field):
    if django_version >= (1, 8, 0):
        return field.is_relation
    else:
        return field.rel is not None

def get_related_model_from_field(field):
    if django_version >= (1, 8, 0):
        return field.related_model
    else:
        return field.rel.to

def get_django_model_field_list(model, parent_name=None, result=None):
    if result is None:
        result = []
    for field in get_fields(model):
        if parent_name:
            result.append('{}.{}'.format(parent_name, field.name))
        else:
            result.append(py2to3._unicode(field.name))
            if is_relation_field(field):
                if parent_name:
                    item_name = '{}.{}'.format(parent_name, field.name)
                else:
                    item_name = field.name
                get_django_model_field_list(get_related_model_from_field(field), item_name, result)

    return result
