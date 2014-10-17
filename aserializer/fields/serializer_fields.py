# -*- coding: utf-8 -*-

from collections import Iterable

from aserializer.utils import py2to3, registry
from aserializer.fields.fields import BaseSerializerField, SerializerFieldValueError


class SerializerObjectField(BaseSerializerField):

    def __init__(self, fields=None, exclude=None, *args, **kwargs):
        super(SerializerObjectField, self).__init__(*args, **kwargs)
        self.only_fields = fields or []
        self.exclude = exclude or []
        self.unknown_error = None
        self.extras = {}
        self._serializer_cls = None

    @staticmethod
    def normalize_serializer_cls(serializer_cls):
        if isinstance(serializer_cls, py2to3.string):
            serializer_cls = registry.get_serializer(serializer_cls)
        return serializer_cls

    def get_serializer_cls(self):
        return self.normalize_serializer_cls(self._serializer_cls)

    def pre_value(self, fields=None, exclude=None, **extras):
        if isinstance(fields, (list, tuple, set)):
            self.only_fields = set(list(self.only_fields) + list(fields))
        if isinstance(exclude, (list, tuple, set)):
            self.exclude = set(list(self.exclude) + list(exclude))
        self.unknown_error = extras.pop('unknown_error', None)
        self.extras = extras

    def get_instance(self):
        return None

    def __get__(self, instance, owner):
        if instance is None:
            return self
        field, field_name = self._get_field_from_instance(instance=instance)
        if field:
            return field.get_instance()
        return self


class SerializerField(SerializerObjectField):

    def __init__(self, serializer, *args, **kwargs):
        super(SerializerField, self).__init__(*args, **kwargs)
        self._serializer_cls = serializer
        self._serializer = None

    def get_instance(self):
        return self._serializer

    def validate(self):
        if self._serializer:
            if not self._serializer.is_valid():
                raise SerializerFieldValueError(self._serializer.errors, field_names=self.names)
        elif self.required:
            raise SerializerFieldValueError(self._error_messages['required'], field_names=self.names)

    def set_value(self, value):
        if value is None:
            self._serializer = None
            return
        if self._serializer is None:
            self._serializer_cls = self.normalize_serializer_cls(self._serializer_cls)
            self._serializer = self._serializer_cls(source=value,
                                                    fields=self.only_fields,
                                                    exclude=self.exclude,
                                                    unknown_error=self.unknown_error,
                                                    **self.extras)
        else:
            self._serializer.initial(source=value)

    def _to_native(self):
        if self._serializer:
            return self._serializer.dump()
        return None

    def _to_python(self):
        if self._serializer:
            return self._serializer.to_dict()
        return None


class ListSerializerField(SerializerObjectField):

    error_messages = {
        'required': 'This list is empty.',
    }

    def __init__(self, serializer, sort_by=None, *args, **kwargs):
        super(ListSerializerField, self).__init__(*args, **kwargs)
        self._serializer_cls = serializer
        self.items = []
        self._python_items = []
        self._native_items = []

        self._sort_by = None
        if sort_by:
            self._sort_by = [sort_by, ] if isinstance(sort_by, py2to3.string) else sort_by

    def validate(self):
        if self.items:
            _errors = []
            for item in self.items:
                if not item.is_valid():
                    _errors.append(item.errors)
            if _errors:
                raise SerializerFieldValueError(_errors)
        elif self.required:
            raise SerializerFieldValueError(self._error_messages['required'], field_names=self.names)

    def get_instance(self):
        return self.items

    def add_item(self, source):
        self._serializer_cls = self.normalize_serializer_cls(self._serializer_cls)
        _serializer = self._serializer_cls(source=source,
                                           fields=self.only_fields,
                                           exclude=self.exclude,
                                           unknown_error=self.unknown_error,
                                           **self.extras)
        self.items.append(_serializer)

    def set_value(self, value):
        self.items[:] = []
        self._native_items[:] = []
        self._python_items[:] = []
        if isinstance(value, Iterable):
            for item in value:
                self.add_item(source=item)

    def _to_native(self):
        if not self._native_items:
            for item in self.items:
                self._native_items.append(item.dump())
            if self._sort_by:
                self._native_items = sorted(self._native_items,
                                            key=lambda item: [item.get(k, None) for k in self._sort_by])
        return self._native_items

    def _to_python(self):
        if not self._python_items:
            for item in self.items:
                self._python_items.append(item.to_dict())
            # TODO: what about deserialization? do we want/need sorting here as well or do we trust the order of items from json?
            # if self._sort_by:
            #     return sorted(unsorted,
            #                   key=lambda item: [getattr(item, k, None) for k in self._sort_by])
        return self._python_items
