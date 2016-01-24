# -*- coding: utf-8 -*-
from collections import Iterable
try:
    from django.db.models.query import QuerySet
    from django.db.models import Manager
except ImportError:
    QuerySet = None
    Manager = None

from aserializer.fields import ListSerializerField
from aserializer.django.utils import get_local_fields, get_related_fields


class RelatedManagerListSerializerField(ListSerializerField):

    def set_value(self, value):
        if value is None:
            return
        elif isinstance(value, Iterable):
            values = value
        elif isinstance(value, (QuerySet, Manager)):
            # if using prefetch_related, we can't use only as it will re-fetch the data
            if not self.extras.get('use_prefetch') and (self.only_fields or self.exclude):
                local_fields = get_local_fields(value.model)
                related_fields = get_related_fields(value.model)
                only_fields = [f.name for f in local_fields]
                if self.only_fields:
                    only_fields = [f for f in only_fields if f in self.only_fields]
                exclude_fields = [f.name for f in local_fields if f.name in self.exclude]
                if exclude_fields:
                    only_fields = [f for f in only_fields if f not in exclude_fields]
                only_fields += [f.name for f in related_fields]
                # .only() returns a QuerySet of RelatedDjangoModel_Deferred objects?
                values = value.only(*only_fields)
            else:
                values = value.all()
        else:
            return
        self.items[:] = []
        self._native_items[:] = []
        self._python_items[:] = []
        for item in values:
            self.add_item(source=item)
