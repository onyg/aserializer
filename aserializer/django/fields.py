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
        if isinstance(value, Iterable):
            values = value
        elif isinstance(value, (QuerySet, Manager)):
            model_fields = get_django_model_field_list(value.model)
            exclude = [f for f in self.exclude if f in model_fields]
            only_fields = [f for f in self.only_fields if f in model_fields]
            values = value.defer(*exclude).only(*only_fields)
        else:
            return
        self.items[:] = []
        self._native_items[:] = []
        self._python_items[:] = []
        for item in values:
            self.add_item(source=item)
