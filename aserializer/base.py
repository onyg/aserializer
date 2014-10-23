# -*- coding: utf-8 -*-

import logging
import copy
from collections import OrderedDict
import json

from aserializer.fields import *
from aserializer.utils import registry, options


logger = logging.getLogger(__name__)


def get_serializer_fields(bases, attrs):
    fields = [(field_name, attrs.pop(field_name)) for field_name, obj in list(py2to3.iteritems(attrs))
              if isinstance(obj, BaseSerializerField)]
    for base in bases[::-1]:
        if hasattr(base, '_base_fields'):
            fields = list(py2to3.iteritems(base._base_fields)) + fields
    return OrderedDict(fields)


class SerializerBase(type):

    def __new__(cls, name, bases, attrs):
        base_fields = get_serializer_fields(bases, attrs)
        if 'Meta' in attrs:
            meta = attrs.pop('Meta')
        else:
            meta = None
        new_class = super(SerializerBase, cls).__new__(cls, name, bases, attrs)
        for field_name, field in base_fields.items():
            cls.add_field(new_class=new_class, name=field_name, field=field)
        setattr(new_class, '_base_fields', base_fields)
        registry.register_serializer(new_class.__name__, new_class)
        setattr(new_class, '_meta', options.SerializerMetaOptions(meta))
        return new_class

    @classmethod
    def add_field(cls, new_class, name, field):
        field.add_name(name)
        setattr(new_class, name, field)
        if field.map_field is not None:
            field.add_name(field.map_field)
            setattr(new_class, field.map_field, field)


class Serializer(py2to3.with_metaclass(SerializerBase)):
    error_messages = {
        'unknown': 'Totally unknown.'
    }

    def __init__(self, source=None, fields=None, exclude=None, unknown_error=False, **extras):
        self.fields = copy.deepcopy(self._base_fields)
        self._data = self.fields
        fields = fields or self._meta.fields
        exclude = exclude or self._meta.exclude
        if fields:
            self.fields = self.filter_fields(only_fields=fields)
        if exclude:
            self.fields = self.exclude_fields(exclude=exclude)
        self._extras = extras
        self.__show_field_list = fields or []
        self.__exclude_field_list = exclude or []
        # self.source_is_invalid = False
        self._handle_unknown_error = unknown_error
        self.parser = self._meta.parser()
        self.initial(source=source)

    def __iter__(self):
        self.to_dict()
        return self._dict_data.__iter__()

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    @classmethod
    def get_fieldnames(cls, seen=None):
        """
        This method returns the map field names of the serializer object including nested field names.
        """
        if seen is None:
            seen = {}
        result = []
        for name, field in cls._base_fields.items():
            map_field_name = field.map_field or name
            result.append((py2to3._unicode(name),py2to3._unicode(map_field_name)))
            if isinstance(field, SerializerObjectField):
                # It is necessary to check for maximum recursions
                if name in seen:
                    if seen[name] == field.get_serializer_cls():
                        continue
                else:
                    seen[name] = field.get_serializer_cls()
                for nested_name, nested_map_field_name in field.get_serializer_cls().get_fieldnames(seen=seen).items():
                    result.append((u'{}.{}'.format(name, nested_name),
                                   u'{}.{}'.format(map_field_name, nested_map_field_name)))
        return OrderedDict(result)

    @property
    def obj(self):
        return self.parser.obj

    @property
    def cleaned_data(self):
        return self.to_dict()

    def initial(self, source):
        """
        The initial method is preparing the serializer and is setting the source values to the fields
        """
        self._errors = None
        self._dict_data = None
        self._dump_data = None
        self.parser.initial(source)
        if self.parser.obj is None:
            return
        source_attr = self.parser.attribute_names
        for field_name, field in self.fields.items():
            if field_name in source_attr:
                _name = field_name
            elif field.map_field and field.map_field in source_attr:
                _name = field.map_field
            else:
                continue
            if isinstance(field, SerializerObjectField):
                only_fields, exclude =  self.get_fields_and_exclude_for_nested(field_name)
                field.pre_value(fields=only_fields,
                                exclude=exclude,
                                unknown_error=self._handle_unknown_error, **self._extras)
            try:
                value = self.parser.get_value(_name)
                field.set_value(self.clean_field_value(field_name, value))
            except IgnoreField:
                field.ignore = True
            else:
                field.ignore = False

    def get_fields_and_exclude_for_nested(self, field_name):
        field_prefix = '{}.'.format(field_name)
        only = ['.'.join(field.split('.')[1:]) for field in self.__show_field_list
                if str(field).startswith(field_prefix)] or None
        exclude = ['.'.join(field.split('.')[1:]) for field in self.__exclude_field_list
                   if str(field).startswith(field_prefix)] or None
        return only, exclude

    def filter_fields(self, only_fields):
        """
        This method filter the current serializer fields dictionary by the list of field names.
        """
        field_names = self.fields.keys()
        only_fields = [str(field_name).split('.')[0] for field_name in only_fields]
        only_fields = list(filter(lambda x: x in field_names, only_fields))
        if len(only_fields) <= 0:
            return self.fields
        return OrderedDict(filter(lambda x: x[1].identity or x[0] in only_fields, self.fields.items()))

    def exclude_fields(self, exclude):
        """
        This method excluding the current serializer fields dictionary by the list of field names.
        """
        field_names = self.fields.keys()
        exclude = list(filter(lambda field_name: field_name in field_names, exclude))
        if len(exclude) <= 0:
            return self.fields
        return OrderedDict(filter(lambda x: x[1].identity or not x[0] in exclude, self.fields.items()))

    def has_method(self, method_name):
        _method = getattr(self, method_name, None)
        return callable(_method)

    def _custom_field_method(self, method_name, field):
        """
        This method calling a method by the giving method_name and returns the result.
        """
        _method = getattr(self, method_name, None)
        if callable(_method):
            return _method(field)
        return None

    def _validate(self):
        """
        This method is calling all validate methods of all fields. If a validate raises a SerializerFieldValueError the
        error will be stored in an dictionary.
        If a field is an identity field it only will be validate if the source object got the attribute.
        """
        self._errors = {}
        source_attrs = self.parser.attribute_names
        for field_name, field in self.fields.items():
            if field.identity and not field_name in source_attrs:
                continue
            label = field_name
            if field_name in source_attrs or field.map_field in source_attrs:
                try:
                    field.validate()
                    self._custom_field_validation(field)
                except SerializerFieldValueError as e:
                    self._errors[label] = e.errors
                if self._handle_unknown_error:
                    if field_name in source_attrs:
                        source_attrs.remove(field_name)
                    elif field.map_field in source_attrs:
                        source_attrs.remove(field.map_field)
            elif field.required:
                if field.has_default:
                    continue
                self._errors[label] = field.error_messages['required']
        if self._handle_unknown_error:
            for attr in source_attrs:
                if attr not in self.get_fieldnames():
                    self._errors[attr] = self.error_messages['unknown']

    def _custom_field_validation(self, field):
        for name in field.names:
            method_name = '{}_validate'.format(name)
            _method = getattr(self, method_name, None)
            if callable(_method):
                _method(field.to_python())

    def update_field(self, field):
        """
        This method updates the instance result lists and dictionaries for one field object.
        """
        for field_name, f in self.fields.items():
            if f == field:
                if self._errors and field_name in self._errors:
                    del self._errors[field_name]
                if self._dump_data is not None:
                    if field_name in self._dump_data:
                        del self._dump_data[field_name]
                    try:
                        self._dump_data[field_name] = self._field_to_native(field_name, field)
                    except IgnoreField:
                        pass
                if self._dict_data is not None and field_name:
                    _name = field.map_field or field_name
                    if _name in self._dict_data:
                        del self._dict_data[_name]
                    try:
                        self._dict_data[_name] = self._field_to_python(field_name, field)
                    except IgnoreField:
                        pass
                break

    def clean_field_value(self, field_name, value):
        """
        This method calls a custom clean_value method if it exists before the value is set to the field object.
        """
        method_name = '{}_clean_value'.format(field_name)
        if self.has_method(method_name):
            return getattr(self, method_name)(value)
        return value

    @property
    def errors(self):
        """
        This property checks if an error is inside of the instance error dictionary and calling the validate method.
        """
        if self._errors is None:
            self._validate()
        return self._errors

    def errors_to_json(self, indent=None):
        return json.dumps(self.errors, indent=indent)

    def is_valid(self):
        """
        This method checkes if an error was inserted.
        """
        if self.errors:
            return False
        else:
            return True

    def to_dict(self):
        """
        Returns a dictionary with the field values for the python env.
        It ingores fields by the IgnoreField exception.
        """
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
        """
        This method returns a dictionary with the field values for a serialization (i.e. json.dumps)
        It ignores fields by the IgnoreField exception and if the field is an action filed.
        """
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

    def to_json(self, indent=None):
        dump = self.dump()
        return json.dumps(dump, indent=indent)

    def _field_to_python(self, field_name, field):
        """
        This method checks if a custom method for the field python value was implemented
        otherwise returns the result of the field method.
        i.g. for the field with the key 'name' def name_to_python(field):
        """
        method_name = '{}_to_python'.format(field_name)
        if self.has_method(method_name):
            return self._custom_field_method(method_name, field)
        else:
            return field.to_python()

    def _field_to_native(self, field_name, field):
        """
        This method checks if a custom method for the field native value was implemented
        otherwise returns the result of the field method.
        i.g. for the field with the key 'name' def name_to_native(field):
        """
        method_name = '{}_to_native'.format(field_name)
        if self.has_method(method_name):
            return self._custom_field_method(method_name, field)
        else:
            return field.to_native()

    def set_value(self, field_name, value):
        setattr(self, field_name, value)

    def get_value(self, field_name):
        return getattr(self, field_name)
