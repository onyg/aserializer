# -*- coding: utf-8 -*-


from .base import CollectionSerializer


class DjangoCollectionSerializer(CollectionSerializer):

    def metadata(self, objects):
        total_count = objects.count()
        _metadata = {}
        _metadata['offset'] = self._offset or 0
        _metadata['limit'] = self._limit or total_count
        _metadata['total_count'] = total_count
        return _metadata

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
        if len(sort) > 0:
            for sort_item in sort:
                sort_field_name = str(sort_item)
                if sort_field_name.startswith('-'):
                    sort_field_name = sort_field_name[1:]
                if sort_field_name not in objects.model._meta.get_all_field_names():
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