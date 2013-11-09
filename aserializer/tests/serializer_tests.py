# -*- coding: utf-8 -*-

import unittest

import uuid
import decimal
from datetime import datetime, date, time
from aserializer.fields import (IntegerField,
                                FloatField,
                                UUIDField,
                                StringField,
                                DatetimeField,
                                DateField,
                                TimeField,
                                SerializerFieldValueError,
                                UrlField,
                                HIDE_FIELD,
                                IgnoreField,
                                TypeField,
                                EmailField,
                                DecimalField,)
from aserializer.base import Serializer




class TestFlatSerializer(Serializer):
    _type = TypeField('test_object')
    id = IntegerField(required=True, identity=True)
    name = StringField(required=True)
    street = StringField(required=False, on_null=HIDE_FIELD)
    uuid_var = UUIDField(required=True)
    maxmin = IntegerField(max_value=10, min_value=6, required=True)
    datetime_var = DatetimeField(required=True)
    date_var = DateField(required=True)
    time_var = TimeField(required=True)
    haus = StringField(required=True, map_field='house')
    url = UrlField(required=True, base='http://www.base.com', default='api')
    action = StringField(required=False, action_field=True)


class SerializerFlatTestCase(unittest.TestCase):

    def test_object_valid_serialize(self):
        class TestObject(object):
            def __init__(self):
                self.id = 1
                self.name = 'NAME'
                self.street = None
                self.uuid_var = '679fadc8-a156-4f7a-8930-0cc216875ac7'
                self.maxmin = 7
                self.datetime_var = datetime.strptime('2013-10-07T20:15:23', '%Y-%m-%dT%H:%M:%S')
                self.date_var = datetime.strptime('2013-10-07T20:15:23', '%Y-%m-%dT%H:%M:%S').date()
                self.time_var = datetime.strptime('2013-10-07T20:15:23', '%Y-%m-%dT%H:%M:%S').time()
                self.house = 'MAP_TO_HAUS'

        serializer = TestFlatSerializer(source=TestObject())
        self.assertTrue(serializer.is_valid())
        self.assertDictEqual(serializer.errors, {})

        self.assertIsInstance(serializer.id, int)
        self.assertEqual(serializer.id, 1)

        self.assertIsInstance(serializer.name, basestring)
        self.assertEqual(serializer.name, 'NAME')

        self.assertIsNone(serializer.street)

        self.assertIsInstance(serializer.uuid_var, uuid.UUID)
        self.assertEqual(serializer.uuid_var, uuid.UUID('679fadc8-a156-4f7a-8930-0cc216875ac7'))

        self.assertIsInstance(serializer.datetime_var, datetime)
        self.assertEqual(serializer.datetime_var, datetime.strptime('2013-10-07T20:15:23', '%Y-%m-%dT%H:%M:%S'))

        self.assertIsInstance(serializer.date_var, date)
        self.assertEqual(serializer.date_var, datetime.strptime('2013-10-07T20:15:23', '%Y-%m-%dT%H:%M:%S').date())

        self.assertIsInstance(serializer.time_var, time)
        self.assertEqual(serializer.time_var, datetime.strptime('2013-10-07T20:15:23', '%Y-%m-%dT%H:%M:%S').time())

        dump_dict = {
            '_type': u'test_object',
            'id': 1,
            'name': u'NAME',
            'uuid_var': u'679fadc8-a156-4f7a-8930-0cc216875ac7',
            'maxmin': 7,
            'datetime_var': u'2013-10-07T20:15:23',
            'date_var': u'2013-10-07',
            'time_var': u'20:15:23',
            'haus': u'MAP_TO_HAUS',
            'url': u'http://www.base.com/api',
        }
        self.assertDictEqual(serializer.dump(), dump_dict)
        to_dict = {
            '_type': u'test_object',
            'action': u'',
            'id': 1,
            'name': u'NAME',
            'uuid_var': uuid.UUID('679fadc8-a156-4f7a-8930-0cc216875ac7'),
            'maxmin': 7,
            'datetime_var': datetime.strptime('2013-10-07T20:15:23', '%Y-%m-%dT%H:%M:%S'),
            'date_var': datetime.strptime('2013-10-07T20:15:23', '%Y-%m-%dT%H:%M:%S').date(),
            'time_var': datetime.strptime('2013-10-07T20:15:23', '%Y-%m-%dT%H:%M:%S').time(),
            'house': u'MAP_TO_HAUS',
            'url': u'http://www.base.com/api',
            'street': None
        }
        self.assertDictEqual(serializer.to_dict(), to_dict)

    def test_serializer_validation(self):
        class TestObject(object):
            def __init__(self):
                self.id = 1
                #self.name = 'NAME' # missiong
                self.street = None
                self.uuid_var = 'wrong-a156-4f7a-8930-0cc216875ac7'
                self.maxmin = 13  # to high
                self.datetime_var = 'no_datetime'
                self.date_var = 'no_date'
                self.time_var = 'no_time'
                self.haus = 'MAP_TO_HAUS'

        serializer = TestFlatSerializer(source=TestObject())
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)
        self.assertIn('uuid_var', serializer.errors)
        self.assertIn('maxmin', serializer.errors)
        self.assertIn('datetime_var', serializer.errors)
        self.assertIn('date_var', serializer.errors)
        self.assertIn('time_var', serializer.errors)
        self.assertNotIn('haus', serializer.errors)

    def test_serializer_set_values_after_validation(self):
        class TestObject(object):
            def __init__(self):
                self.id = 1
                #self.name = 'NAME' #missiong
                self.street = None
                self.uuid_var = 'wrong-a156-4f7a-8930-0cc216875ac7'
                self.maxmin = 13  # to high
                self.datetime_var = 'no_datetime'
                self.date_var = 'no_date'
                self.time_var = 'no_time'
                self.haus = 'MAP_TO_HAUS'

        serializer = TestFlatSerializer(source=TestObject())
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)
        self.assertIn('uuid_var', serializer.errors)
        self.assertIn('maxmin', serializer.errors)
        self.assertIn('datetime_var', serializer.errors)
        self.assertIn('date_var', serializer.errors)
        self.assertIn('time_var', serializer.errors)

        serializer.name = 'NAME'
        serializer.uuid_var = '679fadc8-a156-4f7a-8930-0cc216875ac7'
        serializer.maxmin = 9
        serializer.datetime_var = '2013-10-07T20:15:23'
        serializer.date_var = '2013-10-07'
        serializer.time_var = '20:15:23'
        self.assertTrue(serializer.is_valid())
        self.assertDictEqual(serializer.errors, {})
        serializer.dump()

    def test_serializer_set_values_by_attributes(self):
        serializer = TestFlatSerializer()
        self.assertFalse(serializer.is_valid())
        serializer.id = 12112
        serializer.street = 'Street 23'
        serializer.name = 'NAME'
        serializer.uuid_var = uuid.UUID('679fadc8-a156-4f7a-8930-0cc216875ac7')
        serializer.maxmin = 9
        serializer.datetime_var = datetime.strptime('2013-10-07T20:15:23', '%Y-%m-%dT%H:%M:%S')
        serializer.date_var = datetime.strptime('2013-10-07T20:15:23', '%Y-%m-%dT%H:%M:%S').date()
        serializer.time_var = datetime.strptime('2013-10-07T20:15:23', '%Y-%m-%dT%H:%M:%S').time()
        serializer.haus = 'THE HOUSE'
        self.assertTrue(serializer.is_valid())
        self.assertDictEqual(serializer.errors, {})
        serializer.dump()

    def test_serializer_set_values(self):
        serializer = TestFlatSerializer()
        self.assertFalse(serializer.is_valid())
        serializer.set_value('id', 12121)
        serializer.set_value('street', 'Street 23')
        serializer.set_value('uuid_var', uuid.UUID('679fadc8-a156-4f7a-8930-0cc216875ac7'))
        serializer.set_value('maxmin', 7)
        serializer.set_value('datetime_var', '2013-10-07T20:15:23')
        serializer.set_value('date_var', '2013-10-07')
        serializer.set_value('time_var', '20:15:23')
        serializer.set_value('haus', 'THE HOUSE')
        serializer.set_value('name', 'NAME')
        self.assertTrue(serializer.is_valid())
        self.assertDictEqual(serializer.errors, {})

if __name__ == '__main__':
    unittest.main()