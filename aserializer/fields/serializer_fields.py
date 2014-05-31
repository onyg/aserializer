# -*- coding: utf-8 -*-

from collections import Iterable

from aserializer.fields.fields import BaseSerializerField, SerializerFieldValueError
from aserializer.fields.registry import get_serializer


class SerializerObjectField(BaseSerializerField):

    def __init__(self, fields=None, *args, **kwargs):
        super(SerializerObjectField, self).__init__(*args, **kwargs)
        self.only_fields = fields or []
        self.exclude = []
        self.extras = {}
        self._serializer_cls = None

    @staticmethod
    def normalize_serializer_cls(serializer_cls):
        if isinstance(serializer_cls, basestring):
            serializer_cls = get_serializer(serializer_cls)
        return serializer_cls

    def get_serializer_cls(self):
        return self.normalize_serializer_cls(self._serializer_cls)

    def pre_value(self, fields=None, exclude=None, **extras):
        if isinstance(fields, list):
            self.only_fields = set(list(self.only_fields) + fields)
        self.exclude = exclude
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


class NestedSerializerField(SerializerObjectField):

    def __init__(self, serializer, *args, **kwargs):
        super(NestedSerializerField, self).__init__(*args, **kwargs)
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
        if self._serializer is None:
            self._serializer_cls = self.normalize_serializer_cls(self._serializer_cls)
            self._serializer = self._serializer_cls(source=value,
                                                    fields=self.only_fields,
                                                    exclude=self.exclude,
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

    def __init__(self, serializer, *args, **kwargs):
        super(ListSerializerField, self).__init__(*args, **kwargs)
        self._serializer_cls = serializer
        self.items = []
        self._python_items = []
        self._native_items = []

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
        return self._native_items

    def _to_python(self):
        if not self._python_items:
            for item in self.items:
                self._python_items.append(item.to_dict())
        return self._python_items
