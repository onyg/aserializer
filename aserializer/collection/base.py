# -*- coding: utf-8 -*-

import json

from aserializer.utils import py2to3, registry, options
from aserializer.base import Serializer


class CollectionBase(type):

    def __new__(cls, name, bases, attrs):
        if 'Meta' in attrs:
            meta = attrs.pop('Meta')
        else:
            meta = None
        new_class = super(CollectionBase, cls).__new__(cls, name, bases, attrs)
        setattr(new_class, '_meta', options.CollectionMetaOptions(meta))
        return new_class


class CollectionSerializer(py2to3.with_metaclass(CollectionBase)):
    ITEM_SERIALIZER_CLS = None

    class Meta:
        with_metadata = True
        fields = []
        exclude = []
        sort = []
        metadata_key = '_metadata'
        items_key = 'items'
        offset_key = 'offset'
        limit_key = 'limit'
        total_count_key = 'totalCount'

    def __init__(self, objects, fields=None, exclude=None, sort=None, limit=None, offset=None, **extras):
        self.pre_initial(objects)
        self.ITEM_SERIALIZER_CLS = self._meta.serializer or self.ITEM_SERIALIZER_CLS
        self._serializer_cls = registry.get_serializer(self.ITEM_SERIALIZER_CLS)
        if self._serializer_cls is None or not issubclass(self._serializer_cls, Serializer):
            raise Exception('No item serializer set')
        self.objects = objects if objects is not None else []
        self._fields = fields or self._meta.fields
        self._exclude = exclude or self._meta.exclude
        self._sort = sort or self._meta.sort
        self._limit = limit or 10
        self._offset = offset or 0
        self.with_metadata = self._meta.with_metadata
        self._extras = extras
        self.handle_extras(extras=self._extras)

    def __len__(self):
        return len(self.objects)

    def pre_initial(self, objects):
        pass

    def handle_extras(self, extras):
        pass

    def metadata(self, objects):
        total_count = len(objects)
        if self._offset > total_count:
            self._offset = total_count
        if self._offset >= total_count:
            self._limit = 0
        _metadata = {}
        _metadata[self._meta.offset_key] = self._offset or 0
        _metadata[self._meta.limit_key] = self._limit or total_count
        _metadata[self._meta.total_count_key] = total_count
        return _metadata

    def item(self, obj):
        _serializer = self._serializer_cls(source=obj, fields=self._fields, exclude=self._exclude, **self._extras)
        if self._meta.validation:
            if not _serializer.is_valid():
                return {}
        return _serializer.dump()

    def _pre(self, objects, limit=None, offset=None, sort=None):
        if offset is None:
            offset = 0
        try:
            offset = int(offset)
            limit = int(limit)
        except Exception:
            limit = None
        if sort:
            if not isinstance(sort, list):
                sort = [py2to3._unicode(sort)]
            def get_key(item, k):
                if isinstance(item, dict):
                    return item.get(k, None)
                return getattr(item, k, None)
            for s in reversed(sort):
                reverse = False
                if s.startswith('-'):
                    reverse = True
                    s = s[1:]
                objects = list(sorted(objects, key=lambda item:get_key(item, s), reverse=reverse))
        try:
            if limit:
                objects = objects[offset:(offset + limit)]
        except Exception:
            return {}
        else:
            return objects

    def _items(self, objects):
        objects = self._pre(objects=objects, limit=self._limit, offset=self._offset, sort=self._sort)
        return list(map(lambda o: self.item(obj=o), objects))

    def _generate(self, objects):
        if hasattr(self, 'result'):
            return self.result
        if self.with_metadata:
            self.result = dict()
            self.result[self._meta.metadata_key] = self.metadata(objects)
            self.result[self._meta.items_key] = self._items(objects)
        else:
            self.result = self._items(objects)

    def dump(self):
        self._generate(self.objects)
        return self.result

    def to_json(self, indent=None):
        dump = self.dump()
        return json.dumps(dump, indent=indent)
