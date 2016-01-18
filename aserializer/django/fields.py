# -*- coding: utf-8 -*-
from collections import Iterable
try:
    from django.db.models.query import QuerySet
    from django.db.models import Manager
except ImportError:
    QuerySet = None
    Manager = None

from aserializer.fields import ListSerializerField
from aserializer.django.utils import get_django_model_field_list


class RelatedManagerListSerializerField(ListSerializerField):

    def set_value(self, value):
        if value is None:
            return
        elif isinstance(value, Iterable):
            values = value
        elif isinstance(value, (QuerySet, Manager)):
            model_fields = get_django_model_field_list(value.model)
            exclude = [f for f in self.exclude if f in model_fields]
            only_fields = [f for f in self.only_fields if f in model_fields]
            # from django.db import DEFAULT_DB_ALIAS, connections; connection = connections[DEFAULT_DB_ALIAS]
            # print len(connection.queries_log)
            # TODO: WTF! There are issues with using defer or only with the desired amount of queries...
            # values = value.defer(*exclude).only(*only_fields)
            # values._known_related_objects = {}
            values = value.defer(*only_fields).only(*only_fields)
            # print len(connection.queries_log)
        else:
            return
        self.items[:] = []
        self._native_items[:] = []
        self._python_items[:] = []
        for item in values:
            self.add_item(source=item)
