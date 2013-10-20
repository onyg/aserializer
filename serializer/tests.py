# -*- coding: utf-8 -*-

import unittest

import uuid
from datetime import datetime, date, time
from fields import (IntegerField,
                    FloatField,
                    UUIDField,
                    StringField,
                    DatetimeField,
                    DateField,
                    TimeField,
                    SerializerFieldValueError,
                    UrlSerializerField,
                    HIDE_FIELD,
                    IgnoreField,)


class FieldsTestCase(unittest.TestCase):

    def test_int_field(self):
        int_field = IntegerField(required=True)
        int_field.set_value(23)
        int_field.validate()
        self.assertEqual(int_field.to_python(), 23)
        self.assertEqual(int_field.to_native(), 23)

        int_field = IntegerField(required=True)
        int_field.set_value('24')
        int_field.validate()
        self.assertEqual(int_field.to_python(), 24)
        self.assertEqual(int_field.to_native(), 24)

        int_field = IntegerField(required=True)
        int_field.set_value('int')
        self.assertRaises(SerializerFieldValueError, int_field.validate)

        int_field = IntegerField(required=True, max_value=24, min_value=22)
        int_field.set_value(23)
        int_field.validate()
        self.assertEqual(int_field.to_python(), 23)
        self.assertEqual(int_field.to_native(), 23)

        int_field = IntegerField(required=True, max_value=24, min_value=22)
        int_field.set_value(100)
        self.assertRaises(SerializerFieldValueError, int_field.validate)

        int_field = IntegerField(required=True, max_value=24, min_value=22, default=23)
        self.assertEqual(int_field.to_python(), 23)
        self.assertEqual(int_field.to_native(), 23)

        int_field = IntegerField(required=False, on_null=HIDE_FIELD)
        self.assertRaises(IgnoreField, int_field.to_python)
        self.assertRaises(IgnoreField, int_field.to_native)

    def test_float_field(self):
        float_field = FloatField(required=True)
        float_field.set_value(23.23)
        float_field.validate()
        self.assertEqual(float_field.to_python(), 23.23)
        self.assertEqual(float_field.to_native(), 23.23)

        float_field = FloatField(required=True)
        float_field.set_value('24.24')
        float_field.validate()
        self.assertEqual(float_field.to_python(), 24.24)
        self.assertEqual(float_field.to_native(), 24.24)

        float_field = FloatField(required=True)
        float_field.set_value('float')
        self.assertRaises(SerializerFieldValueError, float_field.validate)

        float_field = FloatField(required=True, max_value=24.5, min_value=22.1)
        float_field.set_value(23.4)
        float_field.validate()
        self.assertEqual(float_field.to_python(), 23.4)
        self.assertEqual(float_field.to_native(), 23.4)

        float_field = FloatField(required=True, max_value=24.5, min_value=22.1)
        float_field.set_value(24.6)
        self.assertRaises(SerializerFieldValueError, float_field.validate)

        float_field = FloatField(required=True, max_value=24.5, min_value=22.1)
        float_field.set_value(21.6)
        self.assertRaises(SerializerFieldValueError, float_field.validate)

        float_field = FloatField(required=True, default=23.23)
        float_field.validate()
        self.assertEqual(float_field.to_python(), 23.23)
        self.assertEqual(float_field.to_native(), 23.23)

        float_field = FloatField(required=False, on_null=HIDE_FIELD)
        self.assertRaises(IgnoreField, float_field.to_python)
        self.assertRaises(IgnoreField, float_field.to_native)

    def test_string_field(self):
        string_field = StringField(required=True)
        string_field.set_value('string')
        string_field.validate()
        self.assertEqual(string_field.to_python(), 'string')
        self.assertEqual(string_field.to_native(), 'string')

        string_field = StringField(required=True)
        string_field.set_value(12)
        self.assertRaises(SerializerFieldValueError, string_field.validate)

        string_field = StringField(required=True, default='a string')
        string_field.validate()
        self.assertEqual(string_field.to_python(), 'a string')
        self.assertEqual(string_field.to_native(), 'a string')

        string_field = StringField(required=False, on_null=HIDE_FIELD)
        self.assertRaises(IgnoreField, string_field.to_python)
        self.assertRaises(IgnoreField, string_field.to_native)


    def test_uuid_field(self):
        uuid_field = UUIDField(required=True)
        uuid_field.set_value(uuid.uuid4())
        uuid_field.validate()
        self.assertIsInstance(uuid_field.to_python(), uuid.UUID)

        uuid_field = UUIDField(required=True)
        uuid_field.set_value('8005ea5e-60b7-4b2a-ab41-a773b8b72e84')
        uuid_field.validate()
        self.assertIsInstance(uuid_field.to_python(), uuid.UUID)
        self.assertEqual(uuid_field.to_python(),  uuid.UUID('8005ea5e-60b7-4b2a-ab41-a773b8b72e84'))
        self.assertEqual(uuid_field.to_native(), '8005ea5e-60b7-4b2a-ab41-a773b8b72e84')

        uuid_field = UUIDField(required=True)
        uuid_field.set_value('nono')
        self.assertRaises(SerializerFieldValueError, uuid_field.validate)

        uuid_field = UUIDField(required=True)
        self.assertRaises(SerializerFieldValueError, uuid_field.validate)

        uuid_field = UUIDField(required=False)
        uuid_field.validate()
        self.assertIsNone(uuid_field.to_python())
        self.assertEqual(uuid_field.to_native(), '')

        uuid_field = UUIDField(required=True, default=uuid.UUID('8005ea5e-60b7-4b2a-ab41-a773b8b72e84'))
        uuid_field.validate()
        self.assertEqual(uuid_field.to_python(),  uuid.UUID('8005ea5e-60b7-4b2a-ab41-a773b8b72e84'))
        self.assertEqual(uuid_field.to_native(), '8005ea5e-60b7-4b2a-ab41-a773b8b72e84')

        uuid_field = UUIDField(required=True, default='8005ea5e-60b7-4b2a-ab41-a773b8b72e84')
        uuid_field.validate()
        self.assertEqual(uuid_field.to_python(),  uuid.UUID('8005ea5e-60b7-4b2a-ab41-a773b8b72e84'))
        self.assertEqual(uuid_field.to_native(), '8005ea5e-60b7-4b2a-ab41-a773b8b72e84')

        uuid_field = UUIDField(required=False, on_null=HIDE_FIELD)
        self.assertRaises(IgnoreField, uuid_field.to_python)
        self.assertRaises(IgnoreField, uuid_field.to_native)

    def test_datetime_field(self):
        dt = datetime.strptime('2013-10-07T22:58:40', '%Y-%m-%dT%H:%M:%S')
        field = DatetimeField(required=True)
        field.set_value(dt)
        field.validate()
        self.assertIsInstance(field.to_python(), datetime)
        self.assertEqual(field.to_python(), dt)
        self.assertEqual(field.to_native(), '2013-10-07T22:58:40')

        field = DatetimeField(required=True)
        field.set_value('2013-10-07T20:15:23')
        field.validate()
        self.assertEqual(field.to_python(), datetime.strptime('2013-10-07T20:15:23', '%Y-%m-%dT%H:%M:%S'))
        self.assertEqual(field.to_native(), '2013-10-07T20:15:23')

        field = DatetimeField(required=True, formats=['%d.%m.%Y %H:%M:%S'])
        field.set_value('07.10.2013 20:15:23')
        field.validate()
        self.assertEqual(field.to_python(), datetime.strptime('2013-10-07T20:15:23', '%Y-%m-%dT%H:%M:%S'))
        self.assertEqual(field.to_native(), '2013-10-07T20:15:23')

        field = DatetimeField(required=True)
        field.set_value('datetime')
        self.assertRaises(SerializerFieldValueError, field.validate)

        dt = datetime.strptime('2013-10-07T22:58:40', '%Y-%m-%dT%H:%M:%S')
        field = DatetimeField(required=True, default=dt)
        field.validate()
        self.assertEqual(field.to_python(), dt)
        self.assertEqual(field.to_native(), '2013-10-07T22:58:40')

        field = DatetimeField(required=True, default='2013-10-07T22:58:40')
        field.validate()
        self.assertEqual(field.to_python(), dt)
        self.assertEqual(field.to_native(), '2013-10-07T22:58:40')

        field = DatetimeField(required=False, on_null=HIDE_FIELD)
        self.assertRaises(IgnoreField, field.to_python)
        self.assertRaises(IgnoreField, field.to_native)

    def test_date_field(self):
        _date = datetime.strptime('2013-10-07T22:58:40', '%Y-%m-%dT%H:%M:%S').date()
        field = DateField(required=True)
        field.set_value(_date)
        field.validate()
        self.assertIsInstance(field.to_python(), date)
        self.assertEqual(field.to_python(), _date)
        self.assertEqual(field.to_native(), '2013-10-07')

        field = DateField(required=True)
        field.set_value('2013-10-07')
        field.validate()
        self.assertEqual(field.to_python(), datetime.strptime('2013-10-07T20:15:23', '%Y-%m-%dT%H:%M:%S').date())
        self.assertEqual(field.to_native(), '2013-10-07')

        field = DateField(required=True)
        field.set_value('date')
        self.assertRaises(SerializerFieldValueError, field.validate)

        field = DateField(required=True, default='2013-10-07')
        field.validate()
        self.assertEqual(field.to_python(), datetime.strptime('2013-10-07T20:15:23', '%Y-%m-%dT%H:%M:%S').date())
        self.assertEqual(field.to_native(), '2013-10-07')

        field = DateField(required=False, on_null=HIDE_FIELD)
        self.assertRaises(IgnoreField, field.to_python)
        self.assertRaises(IgnoreField, field.to_native)


    def test_time_field(self):
        t = datetime.strptime('2013-10-07T22:58:40', '%Y-%m-%dT%H:%M:%S').time()
        field = TimeField(required=True)
        field.set_value(t)
        field.validate()
        self.assertIsInstance(field.to_python(), time)
        self.assertEqual(field.to_python(), t)
        self.assertEqual(field.to_native(), '22:58:40')

        field = TimeField(required=True)
        field.set_value('22:00:40')
        field.validate()
        self.assertEqual(field.to_python(), datetime.strptime('2013-10-07T22:00:40', '%Y-%m-%dT%H:%M:%S').time())
        self.assertEqual(field.to_native(), '22:00:40')

        field = TimeField(required=True)
        field.set_value('time')
        self.assertRaises(SerializerFieldValueError, field.validate)

        t = datetime.strptime('2013-10-07T22:58:40', '%Y-%m-%dT%H:%M:%S').time()
        field = TimeField(required=True, default=t)
        field.validate()
        self.assertEqual(field.to_python(), t)
        self.assertEqual(field.to_native(), '22:58:40')

        field = TimeField(required=True, default='22:58:40')
        field.validate()
        self.assertEqual(field.to_python(), t)
        self.assertEqual(field.to_native(), '22:58:40')

        field = TimeField(required=False, on_null=HIDE_FIELD)
        self.assertRaises(IgnoreField, field.to_python)
        self.assertRaises(IgnoreField, field.to_native)


    def test_url_field(self):
        field = UrlSerializerField(required=True)
        field.set_value('https://www.onyg.de')
        field.validate()
        self.assertEqual(field.to_python(), 'https://www.onyg.de')
        self.assertEqual(field.to_native(), 'https://www.onyg.de')

        field = UrlSerializerField(required=True, base='http://www.onyg.de')
        field.set_value('api')
        field.validate()
        self.assertEqual(field.to_python(), 'http://www.onyg.de/api')
        self.assertEqual(field.to_native(), 'http://www.onyg.de/api')

        field = UrlSerializerField(required=True)
        field.set_value('api')
        self.assertRaises(SerializerFieldValueError, field.validate)

        field = UrlSerializerField(required=True, default='https://www.onyg.de')
        field.validate()
        self.assertEqual(field.to_python(), 'https://www.onyg.de')
        self.assertEqual(field.to_native(), 'https://www.onyg.de')

        field = UrlSerializerField(required=True, default='no url')
        self.assertRaises(SerializerFieldValueError, field.validate)

        field = UrlSerializerField(required=False, on_null=HIDE_FIELD)
        self.assertRaises(IgnoreField, field.to_python)
        self.assertRaises(IgnoreField, field.to_native)




#class SerializerTestCase(unittest.TestCase):
#
#    def test_


if __name__ == '__main__':
    unittest.main()