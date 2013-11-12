# -*- coding: utf-8 -*-


from .base import CollectionSerializer
from .mixins import DjangoRequestMixin


class DjangoCollectionSerializer(DjangoRequestMixin, CollectionSerializer):

    def metadata(self, objects):
        total_count = objects.count()
        _metadata = {}
        _metadata['offset'] = self._offset or 0
        _metadata['limit'] = self._limit or total_count
        _metadata['total_count'] = total_count
        return _metadata

    def get_model_field_list(self, model, parent_name=None, result=[]):
        for item, i in model._meta.get_fields_with_model():
            if parent_name:
                result.append('{}__{}'.format(parent_name, item.name))
            else:
                result.append(str(item.name))
                if item.rel is not None:
                    if parent_name:
                        item_name = '{}__{}'.format(parent_name, item.name)
                    else:
                        item_name = item.name
                    self.get_model_field_list(item.rel.to, item_name, result)
        return result

    def _pre(self, objects, limit=None, offset=None, sort=[]):
        if offset is None:
            offset = 0
        try:
            offset = int(offset)
            limit = int(limit)
        except Exception, e:
            limit = None
        if sort is None or not isinstance(sort, list):
            sort = [str(sort)]
        sort = [unicode(item).replace('.', '__') for item in sort]
        if len(sort) > 0:
            model_fields = self.get_model_field_list(objects.model)
            for sort_item in sort:
                sort_field_name = str(sort_item)
                if sort_field_name.startswith('-'):
                    sort_field_name = sort_field_name[1:]
                if sort_field_name not in model_fields:
                    sort.remove(sort_item)
        try:
            if len(sort) > 0:
                objects = objects.order_by(*sort)
            if limit:
                objects = objects[offset:(offset + limit)]
        except Exception, e:
            return objects.model.objects.none()
        else:
            return objects
