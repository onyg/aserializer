# -*- coding: utf-8 -*-

from aserializer.utils import py2to3
from aserializer.collection.base import CollectionSerializer
from aserializer.django.mixins import DjangoRequestMixin
from aserializer.django.utils import django_required, get_django_model_field_list

try:
    from django.db.models.query import QuerySet
except ImportError:
    QuerySet = None


class DjangoCollectionSerializer(DjangoRequestMixin, CollectionSerializer):
    @django_required()
    def pre_initial(self, objects):
        if not isinstance(objects, QuerySet):
            raise ValueError('Can only handle a django queryset.')

    def metadata(self, objects):
        if objects:
            total_count = objects.count()
        else:
            total_count = 0
        _metadata = {}
        _metadata[self._meta.offset_key] = self._offset or 0
        _metadata[self._meta.limit_key] = self._limit or total_count
        _metadata[self._meta.total_count_key] = total_count
        return _metadata

    def _pre(self, objects, limit=None, offset=None, sort=None):
        if offset is None:
            offset = 0
        try:
            offset = int(offset)
            limit = int(limit)
        except Exception:
            limit = None
        if sort is not None and not isinstance(sort, list):
            sort = [str(sort)]
        _sort = []
        if objects and sort and len(sort) > 0:
            model_fields = get_django_model_field_list(objects.model)
            serializer_fieldnames = self._serializer_cls.get_fieldnames()
            for sort_item in sort:
                sort_field_name = str(sort_item)
                sort_prefix = ''
                if sort_field_name.startswith('-'):
                    sort_prefix = '-'
                    sort_field_name = sort_field_name[1:]
                if sort_field_name in serializer_fieldnames:
                    sort_field_name = serializer_fieldnames[sort_field_name]
                    if sort_field_name in model_fields:
                        _sort.append('{}{}'.format(sort_prefix, sort_field_name))
        try:
            if objects and len(_sort) > 0:
                _sort = [py2to3._unicode(item).replace('.', '__') for item in _sort]
                objects = objects.order_by(*_sort)
            if limit:
                objects = objects[offset:(offset + limit)]
        except Exception:
            return objects.model.objects.none()
        else:
            return objects
