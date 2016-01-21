# -*- coding: utf-8 -*-
from copy import deepcopy

from aserializer.utils.parsers import Parser


class MetaOptions(object):

    def __init__(self, meta):
        self.fields = getattr(meta, 'fields', [])
        self.exclude = getattr(meta, 'exclude', [])


class SerializerMetaOptions(MetaOptions):

    def __init__(self, meta):
        super(SerializerMetaOptions, self).__init__(meta)
        self.parser = getattr(meta, 'parser', Parser)
        # self.model = getattr(meta, 'model', None)
        # self.parents = getattr(meta, 'parents', RelatedParentManager())
        # self.field_args = getattr(meta, 'field_args', {})


class ModelSerializerMetaOptions(SerializerMetaOptions):

    def __init__(self, meta):
        super(ModelSerializerMetaOptions, self).__init__(meta)
        self.model = getattr(meta, 'model', None)
        self.parents = getattr(meta, 'parents', RelatedParentManager())
        self.field_arguments = ModelFieldKwargsHelper(getattr(meta, 'field_kwargs', {}))


class CollectionMetaOptions(MetaOptions):

    def __init__(self, meta):
        super(CollectionMetaOptions, self).__init__(meta)
        self.serializer = getattr(meta, 'serializer', None)
        self.with_metadata = getattr(meta, 'with_metadata', True)
        self.metadata_key = getattr(meta, 'metadata_key', '_metadata')
        self.items_key = getattr(meta, 'items_key', 'items')
        self.offset_key = getattr(meta, 'offset_key', 'offset')
        self.limit_key = getattr(meta, 'limit_key', 'limit')
        self.total_count_key = getattr(meta, 'total_count_key', 'totalCount')
        self.sort = getattr(meta, 'sort', [])
        self.validation = getattr(meta, 'validation', False)


class RelatedParentManager(object):

    def __init__(self):
        self.parents = []

    def get_working_copy(self):
        return deepcopy(self)

    def handle(self, child):
        if child in self.parents:
            return False
        self.parents.append(child)
        return True


class ModelFieldKwargsHelper(object):

    def __init__(self, kw):
        self._kwargs = kw

    def get_kwargs(self, field_name):
        if field_name in self._kwargs:
            return self._kwargs[field_name]
        return {}

    def parse(self, field_name, **kwargs):
        kw = kwargs.copy()
        if field_name in self._kwargs:
            kw.update(**self._kwargs[field_name])
        return kw

    def get_nested_field_kwargs(self, field_name):
        field_prefix = '{}.'.format(field_name)
        kw = {}
        for k, v in self._kwargs.items():
            if str(k).startswith(field_prefix):
                kw['.'.join(k.split('.')[1:])] = v
        return kw
