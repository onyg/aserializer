# -*- coding: utf-8 -*-

from .base import CollectionSerializer


class MongoEngineCollectionSerializer(CollectionSerializer):

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
            limit = 10
        if sort:
            objects = objects.order_by(*sort)
        return objects.skip(offset).limit(limit)
