# -*- coding: utf-8 -*-

import logging
from collections import OrderedDict
import copy
import json
from fields import *

logger = logging.getLogger(__name__)


def _items(d, **kw):
    return iter(getattr(d, 'iteritems')(**kw))

def get_serializer_fields(bases, attrs, with_base_fields=True):
    def items(d, **kw):
        return iter(getattr(d, 'iteritems')(**kw))
    fields = [(field_name, attrs.pop(field_name)) for field_name, obj in list(items(attrs)) if isinstance(obj, BaseSerializerField)]
    for base in bases[::-1]:
        if hasattr(base, '_fields'):
            fields = list(items(base._fields)) + fields
    return OrderedDict(fields)


class SerializerFieldsMetaClass(type):

    def __new__(cls, name, bases, attrs):
        attrs['_fields'] = get_serializer_fields(bases, attrs)
        new_class = super(SerializerFieldsMetaClass, cls).__new__(cls, name, bases, attrs)
        return new_class


def with_fields_metaclass(*bases):
    return SerializerFieldsMetaClass("SerializerFieldsMetaClass", bases, {})


class BaseSerializer(object):
    TYPE = None

    def __init__(self, object, fields=None, **extras):
        self.obj = object
        self.fields = copy.deepcopy(self._fields)
        if fields:
            self.fields = self.filter_only_fields(self.fields, only_fields=fields)
        self._extras = extras
        self._errors = None
        self._dict_data = None
        self._dump_data = None
        self._set_source_to_fields(self.obj)

    def _set_source_to_fields(self, object):
        source_attr = self.get_fieldnames_from_source(object)
        for field_name, field in self.fields.items():
            if field_name in source_attr:
                field.set_value(self.get_value_from_source(self.obj, field_name))

    def get_value_from_source(self, source, field_name):
        if isinstance(source, dict):
            return source.get(field_name)
        else:
            return getattr(source, field_name)

    def has_attribute(self, source, field_name):
        if isinstance(source, dict):
            return source.has_key(field_name)
        else:
            return hasattr(source, field_name)

    def get_fieldnames_from_source(self, source):
        if isinstance(source, dict):
            return source.keys()
        else:
            return dir(source)

    def remove_mandatory_fields_if_necessary(self, obj, fields):
        for field_name, field in fields.items():
            if field.mandatory and not self.has_attribute(obj, field_name):
                fields.pop(field_name)
        return fields

    def filter_only_fields(self, fields, only_fields, mandatory_fields=None):
        only_fields = [field_name.split('.')[0] for field_name in only_fields]
        result = [(field_name, field) for field_name, field in fields.items() if field.mandatory or field_name in only_fields]
        return OrderedDict(result)

    def _validate(self):
        self._errors = {}
        fields = self.remove_mandatory_fields_if_necessary(self.obj, self.fields)
        source_attr = self.get_fieldnames_from_source(self.obj)
        for field_name, field in fields.items():
            label = field.label or field_name
            if field_name in source_attr:
                try:
                    field.validate()
                except SerializerFieldValueError as e:
                    self._errors[label] = e.errors
            elif field.required:
                self._errors[label] = field.error_messages['required']

    @property
    def errors(self):
        if self._errors is None:
            self._validate()
        return self._errors

    def is_valid(self):
        if self.errors:
            return False
        else:
            return True

    def __getattr__(self, name):
        try:
            field = self.fields.get(name)
        except:
            raise AttributeError()
        else:
            if field is None:
                raise AttributeError()
            return field.to_python()

    def to_dict(self):
        if self._dict_data is None:
            self._dict_data = dict()
            for field_name, field in self.fields.items():
                self._dict_data[field_name] = field.to_python()
        return self._dict_data

    def dump(self):
        if self._dump_data is None:
            self._dump_data = dict()
            for field_name, field in self.fields.items():
                self._dump_data[field_name] = field.to_native()
        return self._dump_data

    def to_json(self):
        dump = self.dump()
        return json.dumps(dump, indent=4)


class Serializer(with_fields_metaclass(BaseSerializer)):
    pass


class TestSerializer(Serializer):
    id = IntegerField(required=True, mandatory=True)
    name = StringField(required=True)
    street = StringField(required=False)
    nickname = StringField(required=False)
    uuid = UUIDField(required=True)
    maxmin = IntegerField(max_value=10, min_value=6, required=True)
    created = DatetimeField(required=True)
    bbb = DatetimeField(required=True)
    aaa = DateField(required=True)
    ccc = TimeField(required=True)


class TestObject(object):

    def __init__(self):
        self.id = 12
        self.name = 'HALLO WELT'
        self.street = 'STREET'
        self.nickname = 'WORLD'
        self.uuid = '679fadc8-a156-4f7a-8930-0cc216875ac7'
        self.maxmin = 10
        self.created = datetime.now()
        #self.created = '2013-10-07T22:58:40'
        self.bbb = '2013-10-07T22:58:40'
        self.aaa = '2013-10-07'
        self.ccc = '22:58:40'
        #self.name = 1

if '__main__'==__name__:

    test = TestSerializer(object=TestObject()) #, fields=['name', 'street'])
    if not test.is_valid():
        print 'first in invalid'
        print test.errors
    else:
        print 'first is valid'
        #print test.to_dict()
        #print test.dump()
        print test.bbb
        print test.aaa
        print test.ccc
        print test.to_json()
        test.name = 'HALLO'
        print test.to_json()
        print test.name
    print '-' * 80
    test2 = TestSerializer(object=TestObject())
    print test2.name


    #print test.id
    #print test.uuid
    #print test.to_json()
    #print test.to_dict()
    #print test.dump()

    #dict_data = {'id':'as', 'name':'Hallo'}
    ##dict_obj = dict(**dict_data)
    ##print dir(dict_obj)
    #test2 = TestSerializer(object=dict_data)
    #if not test2.is_valid():
    #    print 'second in invalid'
    #    print test2.errors
    #else:
    #    print 'second is valid'
    #print test2.fields
    #print test3.fields