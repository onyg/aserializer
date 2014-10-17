# -*- coding: utf-8 -*-

import logging

logger = logging.getLogger(__name__)



class MetaOptions(object):

    def __init__(self, meta):
        self.fields = []
        self.exclude = []
        if hasattr(meta, 'fields'):
            self.fields[:] = meta.fields
        if hasattr(meta, 'exclude'):
            self.exclude[:] = meta.exclude



class CollectionMetaOptions(MetaOptions):

    def __init__(self, meta):
        super(CollectionMetaOptions, self).__init__(meta)
        self.serializer = None
        self.with_metadata = True
        self.metadata_key = '_metadata'
        self.items_key = 'items'
        self.offset_key = 'offset'
        self.limit_key = 'limit'
        self.total_count_key = 'totalCount'
        # self.fields = []
        # self.exclude = []
        self.sort = []
        self.validation = False

        if hasattr(meta, 'with_metadata'):
            self.with_metadata = meta.with_metadata
        # if hasattr(meta, 'fields'):
        #     self.fields[:] = meta.fields
        # if hasattr(meta, 'exclude'):
        #     self.exclude[:] = meta.exclude
        if hasattr(meta, 'sort'):
            self.sort[:] = meta.sort
        if hasattr(meta, 'offset_key'):
            self.offset_key = meta.offset_key
        if hasattr(meta, 'limit_key'):
            self.limit_key = meta.limit_key
        if hasattr(meta, 'total_count_key'):
            self.total_count_key = meta.total_count_key
        if hasattr(meta, 'metadata_key'):
            self.metadata_key = meta.metadata_key
        if hasattr(meta, 'items_key'):
            self.items_key = meta.items_key
        if hasattr(meta, 'serializer'):
            self.serializer = meta.serializer
        if hasattr(meta, 'validation'):
            self.validation = meta.validation