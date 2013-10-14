# -*- coding: utf-8 -*-

import logging
from collections import OrderedDict
import inspect
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
        if hasattr(base, 'fields'):
            fields = list(items(base.fields)) + fields
    return OrderedDict(fields)


class SerializerBase(type):

    def __new__(cls, name, bases, attrs):
        base_fields = get_serializer_fields(bases, attrs)
        new_class = super(SerializerBase, cls).__new__(cls, name, bases, attrs)
        for field_name, field in base_fields.items():
            field.add_name(field_name)
            setattr(new_class, field_name, field)
            if field.map_field is not None:
                field.add_name(field.map_field)
                setattr(new_class, field.map_field, field)
        setattr(new_class, 'fields', base_fields)
        return new_class


class Serializer(object):

    __metaclass__ = SerializerBase

    def __init__(self, source=None, fields=None, exclude=None, **extras):
        if fields:
            self.fields = self.filter_only_fields(self.fields, only_fields=fields)
        if exclude:
            self.fields = self.filter_excluded_fields(self.fields, exclude)
        self._extras = extras
        self.initial(source=source)

    def initial(self, source):
        self.obj = source
        self._errors = None
        self._dict_data = None
        self._dump_data = None
        if self.obj is not None:
            self._set_source_to_fields(self.obj)

    def _set_source_to_fields(self, source):
        source_attr = self.get_fieldnames_from_source(source)
        for field_name, field in self.fields.items():
            _name = field.map_field or field_name
            if _name in source_attr:
                try:
                    field.set_value(self.get_value_from_source(self.obj, _name))
                except IgnoreField:
                    pass

    def get_value_from_source(self, source, field_name):
        if isinstance(source, dict):
            value = source.get(field_name)
        else:
            value = getattr(source, field_name)
        value = self.clean_field_value(field_name, value)
        return value

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

    def filter_excluded_fields(self, fields, exlude):
        exlude = [field_name.split('.')[0] for field_name in exlude]
        result = [(field_name, field) for field_name, field in fields.items() if field.identity or not field_name in exlude]
        return OrderedDict(result)

    def _custom_field_methods(self):
        return inspect.getmembers(self, predicate=lambda item: inspect.ismethod(item) and str(item.__name__).endswith('_'))

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
            _name = field.map_field or field_name
            if _name in source_attr:
                try:
                    field.validate()
                except SerializerFieldValueError as e:
                    self._errors[label] = e.errors
            elif field.required:
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
                if self._dict_data is not None:
                    try:
                        self._dict_data[field_name] = self._field_to_python(field_name, field)
                    except IgnoreField:
                        pass


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

    def is_valid(self):
        if self.errors:
            return False
        else:
            return True

    def to_dict(self):
        if self._dict_data is None:
            self._dict_data = dict()
            for field_name, field in self.fields.items():
                try:
                    self._dict_data[field_name] = self._field_to_python(field_name, field)
                except IgnoreField:
                    pass
        return self._dict_data

    def dump(self):
        if self._dump_data is None:
            self._dump_data = dict()
            for field_name, field in self.fields.items():
                try:
                    self._dump_data[field_name] = self._field_to_native(field_name, field)
                except IgnoreField:
                    pass
        return self._dump_data

    def to_json(self):
        dump = self.dump()
        return json.dumps(dump, indent=4)

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


class TestSerializer(Serializer):
    _type = TypeField('test_object')
    id = IntegerField(required=True, identity=True)
    name = StringField(required=True)
    street = StringField(required=False, on_null=HIDE_FIELD)
    nickname = StringField(required=False)
    uuid = UUIDField(required=True)
    maxmin = IntegerField(max_value=10, min_value=6, required=True)
    created = DatetimeField(required=True)
    bbb = DatetimeField(required=True)
    aaa = DateField(required=True)
    ccc = TimeField(required=True)
    haus = StringField(required=True, map_field='house')

    def street_clean_value(self, value):
        return 'Changed {}'.format(value)



class RTest(TestSerializer):
    no = IntegerField(required=False)


class TestObject(object):

    def __init__(self):
        self._type = 'HAHA'
        self.id = 12
        self.name = 'HALLO WELT'
        self.street = None #'STREET'
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
        self.no = 1



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

    test = TestSerializer(source=TestObject()) #, fields=['name', 'street'])
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
        test.street = 'HALLO'
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