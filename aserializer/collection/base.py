# -*- coding: utf-8 -*-

import json

from ..base import Serializer

class CollectionSerializer(object):
    ITEM_SERIALIZER_CLS = None
    WITH_METADATA = True
    FIELDS = []
    EXCLUDE = []

    def __init__(self, objects, fields=None, exclude=None, sort=None, limit=None, offset=None, **extras):
        if self.ITEM_SERIALIZER_CLS is None or not issubclass(self.ITEM_SERIALIZER_CLS, Serializer):
            raise Exception('No item serializer set')
        self.objects = objects
        self._fields = fields or self.FIELDS
        self._exclude = exclude or self.EXCLUDE
        self._sort = sort
        self._limit = limit or 10
        self._offset = offset or 0
        self.with_metadata = self.WITH_METADATA
        self._extras = extras
        self.handle_extras(extras=self._extras)

    def handle_extras(self, extras):
        pass

    def metadata(self, objects):
        total_count = len(objects)
        if self._offset > total_count:
            self._offset = total_count
        if self._offset >= total_count:
            self._limit = 0
        _metadata = {}
        _metadata['offset'] = self._offset or 0
        _metadata['limit'] = self._limit or total_count
        _metadata['total_count'] = total_count
        return _metadata

    def item(self, obj, fields):
        return self.ITEM_SERIALIZER_CLS(source=obj, fields=fields, exclude=self._exclude, **self._extras).dump()

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
        try:
            if limit:
                objects = objects[offset:(offset + limit)]
        except Exception, e:
            return {}
        else:
            return objects

    def _items(self, objects):
        objects = self._pre(objects=objects, limit=self._limit, offset=self._offset, sort=self._sort)
        return map(lambda o: self.item(obj=o, fields=self._fields), objects)

    def _generate(self, objects):
        if hasattr(self, 'result'):
            return self.result
        if self.with_metadata:
            self.result = {}
            self.result['_metadata'] = self.metadata(objects)
            self.result['items'] = self._items(objects)
        else:
            self.result = self._items(objects)

    def dump(self):
        self._generate(self.objects)
        return self.result

    def to_json(self, indent=4):
        dump = self.dump()
        return json.dumps(dump, indent=indent)