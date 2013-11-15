# -*- coding: utf-8 -*-

from .base import CollectionSerializer
from .mixins import DjangoRequestMixin


class DjangoCollectionSerializer(DjangoRequestMixin, CollectionSerializer):

    def metadata(self, objects):
        total_count = objects.count()
        _metadata = {}
        _metadata[self._meta.offset_key] = self._offset or 0
        _metadata[self._meta.limit_key] = self._limit or total_count
        _metadata[self._meta.total_count_key] = total_count
        return _metadata

    def get_model_field_list(self, model, parent_name=None, result=[]):
        for item, i in model._meta.get_fields_with_model():
            if parent_name:
                result.append('{}.{}'.format(parent_name, item.name))
            else:
                result.append(str(item.name))
                if item.rel is not None:
                    if parent_name:
                        item_name = '{}.{}'.format(parent_name, item.name)
                    else:
                        item_name = item.name
                    self.get_model_field_list(item.rel.to, item_name, result)
        return result

    def _pre(self, objects, limit=None, offset=None, sort=None):
        if offset is None:
            offset = 0
        try:
            offset = int(offset)
            limit = int(limit)
        except Exception, e:
            limit = None
        if sort is not None and not isinstance(sort, list):
            sort = [str(sort)]
        _sort = []
        if sort and len(sort) > 0:
            model_fields = self.get_model_field_list(objects.model)
            serializer_fieldnames = self.ITEM_SERIALIZER_CLS.get_fieldnames()
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
            if len(_sort) > 0:
                _sort = [unicode(item).replace('.', '__') for item in _sort]
                objects = objects.order_by(*_sort)
            if limit:
                objects = objects[offset:(offset + limit)]
        except Exception, e:
            return objects.model.objects.none()
        else:
            return objects
