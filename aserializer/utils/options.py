# -*- coding: utf-8 -*-

from aserializer.utils.parsers import Parser



class MetaOptions(object):

    def __init__(self, meta):
        self.fields = getattr(meta, 'fields', [])
        self.exclude = getattr(meta, 'exclude', [])


class SerializerMetaOptions(MetaOptions):

    def __init__(self, meta):
        super(SerializerMetaOptions, self).__init__(meta)
        self.parser = getattr(meta, 'parser', Parser)
        self.model = getattr(meta, 'model', None)
        self.parents = getattr(meta, 'parents', RelatedParentManager())


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
        self.children = list()
        self.root = None

    def add(self, parent, child, map=None):
        if self.root is None:
            self.root = parent
        self.children.append(child)

    def ignore_child(self, parent, child):
        if self.root is None:
            self.root = parent
        if parent is self.root:
            return False
        elif child in self.children:
            return True
        return self.root is child

