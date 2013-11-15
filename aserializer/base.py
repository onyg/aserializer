# -*- coding: utf-8 -*-

import logging
import copy
from collections import OrderedDict
import json
from fields import *
from fields import register_serializer

logger = logging.getLogger(__name__)


def get_serializer_fields(bases, attrs, with_base_fields=True):
    def items(d, **kw):
        return iter(getattr(d, 'iteritems')(**kw))
    fields = [(field_name, attrs.pop(field_name)) for field_name, obj in list(items(attrs)) if isinstance(obj, BaseSerializerField)]
    for base in bases[::-1]:
        if hasattr(base, 'fields'):
            fields = list(items(base.fields)) + fields
    return OrderedDict(fields)


class SerializerBase(type):

    def __new__(cls, name, bases, attrs):
        base_fields = get_serializer_fields(bases, attrs)
        new_class = super(SerializerBase, cls).__new__(cls, name, bases, attrs)
        for field_name, field in base_fields.items():
            cls.add_field(new_class=new_class, name=field_name, field=field)
        setattr(new_class, '_base_fields', base_fields)
        register_serializer(new_class.__name__, new_class)
        return new_class

    @classmethod
    def add_field(cls, new_class, name, field):
        field.add_name(name)
        setattr(new_class, name, field)
        if field.map_field is not None:
            field.add_name(field.map_field)
            setattr(new_class, field.map_field, field)


class Serializer(object):

    __metaclass__ = SerializerBase

    def __init__(self, source=None, fields=None, exclude=None, **extras):
        self.fields = copy.deepcopy(self._base_fields)
        self._data = self.fields
        if fields:
            self.fields = self.filter_only_fields(only_fields=fields)
        if exclude:
            self.fields = self.filter_excluded_fields(exclude=exclude)
        self._extras = extras
        self.__show_field_list = fields or []
        self.__exclude_field_list = exclude or []
        self.source_is_invalid = False
        self.initial(source=source)

    def __iter__(self):
        self.to_dict()
        return self._dict_data.__iter__()

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    @classmethod
    def get_fieldnames(cls):
        result = []
        for name, field in cls._base_fields.items():
            map_field_name = field.map_field or name
            result.append((name, map_field_name))
            if isinstance(field, SerializerObjectField):
                for nested_name, nested_map_field_name in field.get_serializer_cls().get_fieldnames().items():
                    result.append(('{}.{}'.format(name, nested_name),
                                   '{}.{}'.format(map_field_name, nested_map_field_name)))
        return OrderedDict(result)


    def initial(self, source):
        if isinstance(source, basestring):
            if not isinstance(source, unicode):
                source = unicode(source, 'utf-8')
            try:
                self.obj = json.loads(source)
            except ValueError:
                self.obj = object()
        else:
            self.obj = source
        self._errors = None
        self._dict_data = None
        self._dump_data = None
        if self.obj is not None:
            self._set_source_to_fields(self.obj)

    def _set_source_to_fields(self, source):
        source_attr = self.get_fieldnames_from_source(source)
        for field_name, field in self.fields.items():
            if field_name in source_attr:
                _name = field_name
            elif field.map_field and field.map_field in source_attr:
                _name = field.map_field
            else:
                continue
            if isinstance(field, SerializerObjectField):
                only_fields, exclude =  self.get_fields_and_exclude_for_nested(field_name)
                field.pre_value(fields=only_fields, exclude=exclude, **self._extras)
            try:
                value = self.get_value_from_source(self.obj, _name)
                field.set_value(self.clean_field_value(field_name, value))
            except IgnoreField:
                field.ignore = True
            else:
                field.ignore = False

    @staticmethod
    def get_value_from_source(source, field_name):
        if isinstance(source, dict):
            value = source.get(field_name, None)
        else:
            value = getattr(source, field_name, None)
        return value

    @staticmethod
    def has_attribute(source, field_name):
        if isinstance(source, dict):
            return source.has_key(field_name)
        else:
            return hasattr(source, field_name)

    @staticmethod
    def get_fieldnames_from_source(source):
        if isinstance(source, dict):
            return source.keys()
        else:
            return dir(source)

    def get_fields_and_exclude_for_nested(self, field_name):
        field_prefix = '{}.'.format(field_name)
        only = ['.'.join(field.split('.')[1:]) for field in self.__show_field_list if str(field).startswith(field_prefix)] or None
        exclude = ['.'.join(field.split('.')[1:]) for field in self.__exclude_field_list if str(field).startswith(field_prefix)] or None
        return only, exclude

    def filter_only_fields(self, only_fields):
        field_names = self.fields.keys()
        only_fields = [str(field_name).split('.')[0] for field_name in only_fields]
        only_fields = filter(lambda field_name: field_name in field_names, only_fields)
        if len(only_fields) <= 0:
            return self.fields
        return OrderedDict(filter(lambda (field_name, field): field.identity or field_name in only_fields, self.fields.items()))

    def filter_excluded_fields(self, exclude):
        field_names = self.fields.keys()
        exclude = filter(lambda field_name: field_name in field_names, exclude)
        if len(exclude) <= 0:
            return self.fields
        return OrderedDict(filter(lambda (field_name, field): field.identity or not field_name in exclude, self.fields.items()))

    def has_method(self, name):
        _method = getattr(self, name, None)
        return callable(_method)

    def _custom_field_method(self, name, field):
        _method = getattr(self, name, None)
        if callable(_method):
            return _method(field)
        return None

    def _validate(self):
        self._errors = {}
        source_attr = self.get_fieldnames_from_source(self.obj)
        for field_name, field in self.fields.items():
            if field.identity and not field_name in source_attr:
                continue
            label = field_name
            if field_name in source_attr or field.map_field in source_attr:
                try:
                    field.validate()
                except SerializerFieldValueError as e:
                    self._errors[label] = e.errors
            elif field.required:
                if field.has_default:
                    continue
                self._errors[label] = field.error_messages['required']

    def update_field(self, field):
        for field_name, f in self.fields.items():
            if f == field:
                if self._errors and field_name in self._errors:
                    del self._errors[field_name]
                if self._dump_data is not None:
                    try:
                        self._dump_data[field_name] = self._field_to_native(field_name, field)
                    except IgnoreField:
                        pass
                if self._dict_data is not None and field_name:
                    _name = field.map_field or field_name
                    try:
                        self._dict_data[_name] = self._field_to_python(field_name, field)
                    except IgnoreField:
                        pass
                break

    def clean_field_value(self, field_name, value):
        method_name = '{}_clean_value'.format(field_name)
        if self.has_method(method_name):
            return getattr(self, method_name)(value)
        return value

    @property
    def errors(self):
        if self._errors is None:
            self._validate()
        return self._errors

    def errors_to_json(self, indent=4):
        return json.dumps(self.errors, indent=indent)

    def is_valid(self):
        if self.errors:
            return False
        else:
            return True

    def to_dict(self):
        if self._dict_data is None:
            self._dict_data = dict()
            for field_name, field in self.fields.items():
                _name = field.map_field or field_name
                try:
                    self._dict_data[_name] = self._field_to_python(field_name, field)
                except IgnoreField:
                    pass
        return self._dict_data

    def dump(self):
        if self._dump_data is None:
            self._dump_data = dict()
            for field_name, field in self.fields.items():
                if field.action_field:
                    continue
                try:
                    self._dump_data[field_name] = self._field_to_native(field_name, field)
                except IgnoreField:
                    pass
        return self._dump_data

    def to_json(self, indent=4):
        dump = self.dump()
        return json.dumps(dump, indent=indent)

    def _field_to_python(self, field_name, field):
        method_name = '{}_to_python'.format(field_name)
        if self.has_method(method_name):
            return self._custom_field_method(method_name, field)
        else:
            return field.to_python()

    def _field_to_native(self, field_name, field):
        method_name = '{}_to_native'.format(field_name)
        if self.has_method(method_name):
            return self._custom_field_method(method_name, field)
        else:
            return field.to_native()

    def set_value(self, field_name, value):
        setattr(self, field_name, value)

    def get_value(self, field_name):
        return getattr(self, field_name)
