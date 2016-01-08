# -*- coding: utf-8 -*-
from collections import Iterable
try:
    from django.db.models.query import QuerySet
    from django.db.models import Manager
except ImportError:
    QuerySet = None
    Manager = None

from aserializer.fields import ListSerializerField


class RelatedManagerListSerializerField(ListSerializerField):

    def set_value(self, value):
        if isinstance(value, Iterable):
            values = value
        elif isinstance(value, (QuerySet, Manager)):
            values = value.defer(*self.exclude).only(*self.only_fields)
        else:
            return
        self.items[:] = []
        self._native_items[:] = []
        self._python_items[:] = []
        for item in values:
            self.add_item(source=item)
