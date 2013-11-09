# -*- coding: utf-8 -*-

import logging
import copy
from collections import OrderedDict
import json
from fields import *
from fields import register_serializer

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
            self.fields = self.filter_only_fields(self.fields, only_fields=fields)
        if exclude:
            self.fields = self.filter_excluded_fields(self.fields, exclude)
        self._extras = extras
        self.__show_field_list = fields or []
        self.__exclude_field_list = exclude or []
        self.source_is_invalid = False
        self.initial(source=source)

    def __iter__(self):
        self.to_dict()
        return self._dict_data.__iter__()

    #def __getitem__(self, key):
    #    return self.to_dict()[key]
    #
    #def __setitem__(self, key, value):
    #    setattr(self, key, value)
    #    #field = getattr(self, )
    #    #if key in self.fields:
    #    #    self._set_field(key, value)

    def initial(self, source):
        if isinstance(source, basestring):
            if not isinstance(source, unicode):
                source = unicode(source, 'utf-8')
            try:
                self.obj = json.loads(source)
            except ValueError:
                self.obj = object()
                #self.source_is_invalid + True
                #raise ValueError('Source is not serializable.')
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
                only_fields, exclude =  self.get_nested_fields(field_name)
                field.pre_value(fields=only_fields, exclude=exclude, **self._extras)
            try:
                value = self.get_value_from_source(self.obj, _name)
                field.set_value(self.clean_field_value(field_name, value))
            except IgnoreField:
                pass

    def get_value_from_source(self, source, field_name):
        if isinstance(source, dict):
            value = source.get(field_name)
        else:
            value = getattr(source, field_name)
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

    def get_nested_fields(self, field_name):
        field_prefix = '{}.'.format(field_name)
        only = ['.'.join(field.split('.')[1:]) for field in self.__show_field_list if str(field).startswith(field_prefix)] or None
        exclude = ['.'.join(field.split('.')[1:]) for field in self.__exclude_field_list if str(field).startswith(field_prefix)] or None
        return only, exclude

    def filter_only_fields(self, fields, only_fields, identity_fields=None):
        field_names = fields.keys()
        only_fields = [str(field_name).split('.')[0] for field_name in only_fields]
        only_fields = filter(lambda field_name: field_name in field_names, only_fields)
        if len(only_fields) <= 0:
            return fields
        return OrderedDict(filter(lambda (field_name, field): field.identity or field_name in only_fields, fields.items()))

    def filter_excluded_fields(self, fields, exclude):
        field_names = fields.keys()
        exclude = filter(lambda field_name: field_name in field_names, exclude)
        if len(exclude) <= 0:
            return fields
        return OrderedDict(filter(lambda (field_name, field): field.identity or not field_name in exclude, fields.items()))

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
        #for field_name in field.names:
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





class NestSerializer(Serializer):

    class NestNestSerializer(Serializer):
        _type = TypeField('nest_nest')
        ida = IntegerField(required=True, identity=True)
        namea = StringField(required=True)
        streeta = StringField(required=False, on_null=HIDE_FIELD)
        nicknamea = StringField(required=False)
        uuida = UUIDField(required=True)

    _type = TypeField('emb')
    id = IntegerField(required=True, identity=True)
    name = StringField(required=True)
    number = IntegerField(required=True)
    nestnest = NestedSerializerField(NestNestSerializer, on_null=HIDE_FIELD)

class NestListSerializer(Serializer):

    _type = TypeField('emb')
    id = IntegerField(required=True, identity=True)
    name = StringField(required=True)
    number = IntegerField(required=True)
    #haha = StringField(required=True)
    dec = DecimalField(required=True, decimal_places=2)

class TestSerializer(Serializer):
    _type = TypeField('test_object')
    id = IntegerField(required=True, identity=True)
    name = StringField(required=True)
    street = StringField(required=False, on_null=HIDE_FIELD)
    nickname = StringField(required=True)
    uuid = UUIDField(required=True)
    maxmin = IntegerField(max_value=10, min_value=6, required=True)
    created = DatetimeField(required=True)
    bbb = DatetimeField(required=True)
    aaa = DateField(required=True)
    ccc = TimeField(required=True)
    haus = StringField(required=True, map_field='house')
    url = UrlField(required=True, base='http://www.base.com', default='api')
    action = StringField(required=False, action_field=True)
    nest = NestedSerializerField('NestSerializer', required=True)
    email = EmailField(required=True)
    list_value = ListSerializerField('NestListSerializer', required=True)

    def street_clean_value(self, value):
        return 'Changed {}'.format(value)



class RTest(TestSerializer):
    no = IntegerField(required=False)


class LittleTestSerialzer(Serializer):
    _type = TypeField('test_object')
    id = IntegerField(required=True, identity=True)
    name = StringField(required=True)
    street = StringField(required=False, on_null=HIDE_FIELD)
    nickname = StringField(required=True)

class NestNestObject(object):

    def __init__(self):
        self.ida = 12
        self.namea = 'HALLO WELT'
        self.streeta = None #'STREET'
        self.nicknamea = 'WORLD'
        self.uuida = '679fadc8-a156-4f7a-8930-0cc216875ac7'

class NestObject(object):

    def __init__(self):
        self.id = 122
        self.name = 'test nest'
        self.nestnest = NestNestObject()
        self.number = '12a'

class NestListObject(object):

    def __init__(self):
        self.id = 122
        self.name = 'test list nest'
        self.number = 12
        self.dec = '23.012'

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
        self.bbb = 'asas' #'2013-10-07T22:58:40'
        self.aaa = 'sd'#'2013-10-07'
        self.ccc = 'wee'#'22:58:40'
        self.house = 'ENGLISCH'
        #self.name = 1
        self.no = 1
        self.action = 'ACTION'

        self.nest = NestObject()
        self.email = '__as@jasak.de'
        self.list_value = []
        for a in range(3):
            self.list_value.append(NestListObject())


class TestObject2(object):

    def __init__(self):
        self.id = 12
        self.name = 'ggg'
        self.street = 'ggg'
        self.nickname = 'ggg'
        self.uuid = '779fadc8-a156-4f7a-8930-0cc216875ac7'
        self.maxmin = 6
        self.created = datetime.now()
        #self.created = '2013-10-07T22:58:40'
        self.bbb = '2013-10-07T22:58:40'
        self.aaa = '2013-10-07'
        self.ccc = '22:58:40'
        #self.name = 1
        self.nest = NestObject()
        self.list_value = [NestListObject()]


if '__main__'==__name__:

    #bla_dict = dict(id=101, name='dictname', street='dictstreet', nickname='thenickname')
    #
    #dicttest = LittleTestSerialzer(bla_dict)
    #if not dicttest.is_valid():
    #    print 'DICT INVALID'
    #    print dicttest.errors_to_json()
    #else:
    #    print 'DICT VALID'
    #    print dicttest.to_json()
    #
    #bla_string = '{"id": 121, "name":"the name", "street":"stringstreet", "nickname":"thenickname"}'
    #string_test = LittleTestSerialzer(bla_string)
    #if not string_test.is_valid():
    #    print 'STRING INVALID'
    #    print string_test.errors_to_json()
    #else:
    #    print 'STRING VALID'
    #    print string_test.to_json()

    test = TestSerializer(source=TestObject(), fields=[], exclude=[])#, 'nest.nestnest.uuida'])
    if not test.is_valid():
        print 'first in invalid'
        #print test.errors
        print test.errors_to_json()
    else:
        print 'first is valid'
        print test.to_json()
        print test.bbb
        print test.aaa
        print test.ccc
        print test.name
        test.bbb = '2013-10-07T22:58:40'
        #test.street = 'HALLO'
        #print test.to_json()
        #print test.name
        #print test.nest.name
        #for value in test.list_value:
        #    for item in value:
        #        print value[item]
        #print test.list_value[0].name
        #test.list_value[0].name = 'RONALD'
        #print test.to_json()
    #print test.name
    ##print test.ron
    #print '-' * 60
    #print test.name
    #test2 = TestSerializer()
    #print test2.name or 'test 2.name NONE'
    #print '-' * 60
    #print test.name or 'test.name None'
    ##print test.ron
    ##print test2.ron
    #print test.street
    #
    #test.name = '12345'
    #test2.name = '54321'
    #print test.name
    #print test2.name
    #print test.to_json()
    #if not test2.is_valid():
    #    print test2.errors_to_json()
    #else:
    #    print test2.to_json()

    #print test.to_json()

    #if test2.is_valid():
    #    print 'second is valid'
    #    print test2.to_json()
    #else:
    #    print 'second is invalid'
    #    print test2.errors_to_json()
    #print '-' * 80
    #test.haus = 'DEUTSCH'
    #print test.to_json()
    #print test.to_dict()
    #print test.action
    #print test.nest.name
    #test.nest.name = 'hallo'
    #print test.nest.name
    #
    #for key in test:
    #    print key
    ##print dict(test.nest)
    #print test.to_json()

    #test2 = TestSerializer(object=None) #, fields=['name', 'street'])

    #test2 = TestSerializer(source=TestObject2()) #, fields=['name', 'street'])
    #if not test2.is_valid():
    #    print '2 first in invalid'
    #    print test2.errors_to_json()
    #else:
    #    print '2 first is valid'
    #    print test2.to_json()
    #print '-' * 80
    ##print test.to_json()
    ##print test2.to_json()
    #test2.house = 'VALUE HOUSE'
    #print test2.errors_to_json()
    #test2.email = 'test@test.de'
    #print test2.to_json()




    #print test.id
    #print test.uuid
    #test.uuid = uuid.UUID('879fadc8-a156-4f7a-8930-0cc216875ac7')
    #print test.uuid
    #print test2.uuid
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