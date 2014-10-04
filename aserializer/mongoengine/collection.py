# -*- coding: utf-8 -*-

from aserializer.collection.base import CollectionSerializer


class MongoEngineCollectionSerializer(CollectionSerializer):

    def metadata(self, objects):
        total_count = objects.count()
        _metadata = dict()
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
            limit = 10

        if sort is not None and not isinstance(sort, list):
            sort = [str(sort)]
        _sort = []
        if sort and len(sort) > 0:
            serializer_fieldnames = self._serializer_cls.get_fieldnames()
            for sort_item in sort:
                sort_field_name = str(sort_item)
                sort_prefix = ''
                if sort_field_name.startswith('-'):
                    sort_prefix = '-'
                    sort_field_name = sort_field_name[1:]
                if sort_field_name in serializer_fieldnames:
                    sort_field_name = serializer_fieldnames[sort_field_name]
                    _sort.append('{}{}'.format(sort_prefix, sort_field_name))
        if _sort:
            objects = objects.order_by(*_sort)
        return objects.skip(offset).limit(limit)
