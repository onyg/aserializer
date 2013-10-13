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
        if hasattr(base, 'base_fields'):
            fields = list(items(base.base_fields)) + fields
    return OrderedDict(fields)


class SerializerBase(type):

    def __new__(cls, name, bases, attrs):
        base_fields = get_serializer_fields(bases, attrs)
        new_class = super(SerializerBase, cls).__new__(cls, name, bases, attrs)
        for field_name, field in base_fields.items():
            setattr(new_class, field_name, field)
            if field.map_field is not None:
                setattr(new_class, field.map_field, field)
        setattr(new_class, 'fields', base_fields)
        return new_class


class Serializer(object):
    TYPE = None
    __metaclass__ = SerializerBase

    def __init__(self, object, fields=None, **extras):
        self.obj = object
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
            _name = field.map_field or field_name
            if _name in source_attr:
                field.set_value(self.get_value_from_source(self.obj, _name))

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

    def filter_only_fields(self, fields, only_fields, identity_fields=None):
        only_fields = [field_name.split('.')[0] for field_name in only_fields]
        result = [(field_name, field) for field_name, field in fields.items() if field.identity or field_name in only_fields]
        return OrderedDict(result)

    def _validate(self):
        self._errors = {}
        source_attr = self.get_fieldnames_from_source(self.obj)
        for field_name, field in self.fields.items():
            if field.identity and not field_name in source_attr:
                continue
            label = field_name
            _name = field.map_field or field_name
            if _name in source_attr:
                try:
                    field.validate()
                except SerializerFieldValueError as e:
                    self._errors[label] = e.errors
            elif field.required:
                self._errors[label] = field.error_messages['required']

    def _update_field(self, field):
        for field_name, f in self.fields.items():
            if f == field:
                if self._errors and field_name in self._errors:
                    del self._errors[field_name]
                if self._dump_data and field_name in self._dump_data:
                    self._dump_data[field_name] = field.to_native()
                if self._dict_data and field_name in self._dict_data:
                    self._dict_data[field_name] = field.to_python()

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




class TestSerializer(Serializer):
    id = IntegerField(required=True, identity=True)
    name = StringField(required=True)
    street = StringField(required=False)
    nickname = StringField(required=False)
    uuid = UUIDField(required=True)
    maxmin = IntegerField(max_value=10, min_value=6, required=True)
    created = DatetimeField(required=True)
    bbb = DatetimeField(required=True)
    aaa = DateField(required=True)
    ccc = TimeField(required=True)
    haus = StringField(required=True, map_field='house')


class TestObject(object):

    def __init__(self):
        self.id = 12
        self.name = 'HALLO WELT'
        self.street = 'STREET'
        self.nickname = 'WORLD'
        self.uuid = '679fadc8-a156-4f7a-8930-0cc216875ac7'
        #self.uuid = 'asasas'
        self.maxmin = 10
        self.created = datetime.now()
        #self.created = '2013-10-07T22:58:40'
        self.bbb = '2013-10-07T22:58:40'
        self.aaa = '2013-10-07'
        self.ccc = '22:58:40'
        self.house = 'ENGLISCH'
        #self.name = 1


class TestObject2(object):

    def __init__(self):
        self.id = 12
        self.name = 'ggg'
        self.street = 'ggg'
        self.nickname = 'ggg'
        self.uuid = '679fadc8-a156-4f7a-8930-0cc216875ac7-'
        self.maxmin = 6
        self.created = datetime.now()
        #self.created = '2013-10-07T22:58:40'
        self.bbb = '2013-10-07T22:58:40'
        self.aaa = '2013-10-07'
        self.ccc = '22:58:40'
        #self.name = 1


if '__main__'==__name__:

    test = TestSerializer(object=TestObject()) #, fields=['name', 'street'])
    print test.name
    if not test.is_valid():
        print 'first in invalid'
        print test.errors
    else:
        print 'first is valid'
        print test.to_json()
        #print test.bbb
        #print test.aaa
        #print test.ccc
        #test.name = 'HALLO'
        #print test.to_json()
        #print test.name
    print '-' * 80
    test.haus = 'DEUTSCH'
    print test.to_json()

    #test2 = TestSerializer(object=None) #, fields=['name', 'street'])
    #
    ##test2 = TestSerializer(object=TestObject2()) #, fields=['name', 'street'])
    #if not test2.is_valid():
    #    print 'first in invalid'
    #    print test2.errors
    #else:
    #    print 'first is valid'
    #    print test2.to_json()
    #print '-' * 80
    #print test.to_json()
    #print test2.to_json()




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