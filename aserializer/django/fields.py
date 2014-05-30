# -*- coding: utf-8 -*-

import logging

from aserializer.fields import ListSerializerField

logger = logging.getLogger(__name__)


class RelatedManagerListSerializerField(ListSerializerField):

    def set_value(self, value):
        self.items[:] = []
        self._native_items[:] = []
        self._python_items[:] = []
        # if isinstance(value, Iterable):
        for item in value.all():
            self.add_item(source=item)

