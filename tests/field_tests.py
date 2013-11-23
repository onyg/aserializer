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
                                DecimalField,
                                BooleanField,
                                ChoiceField,
                                ListField,)


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
        self.assertRaises(IgnoreField, int_field.to_native)
        self.assertIsNone(int_field.to_python())

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
        self.assertRaises(IgnoreField, float_field.to_native)
        self.assertIsNone(float_field.to_python())

    def test_decimal_field(self):
        field = DecimalField(required=True, decimal_places=2)
        field.set_value(23.23)
        field.validate()
        self.assertEqual(field.to_python(), decimal.Decimal('23.23'))
        self.assertEqual(field.to_native(), 23.23)

        field = DecimalField(required=True)
        field.set_value('float')
        self.assertRaises(SerializerFieldValueError, field.validate)

        field = DecimalField(required=True, decimal_places=1, max_value=24.5, min_value=22.1)
        field.set_value(23.4)
        field.validate()
        self.assertEqual(field, 23.4)
        self.assertEqual(field.to_python(), decimal.Decimal('23.4'))
        self.assertEqual(field.to_native(), 23.4)

        field = DecimalField(required=True, decimal_places=2, output=DecimalField.OUTPUT_AS_STRING)
        field.set_value(23.42)
        field.validate()
        self.assertEqual(field, '23.42')
        self.assertEqual(field.to_python(), decimal.Decimal('23.42'))
        self.assertEqual(field.to_native(), '23.42')

        field = DecimalField(required=True, decimal_places=1, output='no_valid_output')
        field.set_value(23.4)
        field.validate()
        self.assertEqual(field, 23.4)
        self.assertEqual(field.to_python(), decimal.Decimal('23.4'))
        self.assertEqual(field.to_native(), 23.4)

        field = DecimalField(required=True, max_value=24.5, min_value=22.1)
        field.set_value(24.6)
        self.assertRaises(SerializerFieldValueError, field.validate)

        field = DecimalField(required=True, max_value=24.5, min_value=22.1)
        field.set_value(21.6)
        self.assertRaises(SerializerFieldValueError, field.validate)

        field = DecimalField(required=True, default=23.23)
        field.validate()
        self.assertEqual(field.to_python(), decimal.Decimal('23.23'))
        self.assertEqual(field.to_native(), 23.23)

        field = DecimalField(required=True, default=decimal.Decimal('123.123'))
        field.validate()
        self.assertEqual(field.to_python(), decimal.Decimal('123.123'))
        self.assertEqual(field.to_native(), 123.123)

        field = DecimalField(required=True, decimal_places=5)
        field.set_value(decimal.Decimal('9.4'))
        field.validate()
        self.assertEqual(field.to_python(), decimal.Decimal('9.40000'))
        self.assertEqual(field.to_native(), 9.40000)

        field = DecimalField(required=False, on_null=HIDE_FIELD)
        self.assertRaises(IgnoreField, field.to_native)
        self.assertIsNone(field.to_python())

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
        self.assertRaises(IgnoreField, string_field.to_native)
        self.assertIsNone(string_field.to_python())

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
        self.assertRaises(IgnoreField, uuid_field.to_native)
        self.assertIsNone(uuid_field.to_python())

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
        self.assertRaises(IgnoreField, field.to_native)
        self.assertIsNone(field.to_python())

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
        self.assertRaises(IgnoreField, field.to_native)
        self.assertIsNone(field.to_python())

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
        self.assertRaises(IgnoreField, field.to_native)
        self.assertIsNone(field.to_python())

    def test_url_field(self):
        field = UrlField(required=True)
        field.set_value('https://www.onyg.de')
        field.validate()
        self.assertEqual(field.to_python(), 'https://www.onyg.de')
        self.assertEqual(field.to_native(), 'https://www.onyg.de')

        field = UrlField(required=True, base='http://www.onyg.de')
        field.set_value('api')
        field.validate()
        self.assertEqual(field.to_python(), 'http://www.onyg.de/api')
        self.assertEqual(field.to_native(), 'http://www.onyg.de/api')

        field = UrlField(required=True)
        field.set_value('api')
        self.assertRaises(SerializerFieldValueError, field.validate)

        field = UrlField(required=True, default='https://www.onyg.de')
        field.validate()
        self.assertEqual(field.to_python(), 'https://www.onyg.de')
        self.assertEqual(field.to_native(), 'https://www.onyg.de')

        field = UrlField(required=True, default='no url')
        self.assertRaises(SerializerFieldValueError, field.validate)

        field = UrlField(required=False, on_null=HIDE_FIELD)
        self.assertRaises(IgnoreField, field.to_native)
        self.assertIsNone(field.to_python())

    def test_email_field(self):
        field = EmailField(required=True)
        field.set_value('test@test.de')
        field.validate()
        self.assertEqual(field.to_python(), 'test@test.de')
        self.assertEqual(field.to_native(), 'test@test.de')

        field = EmailField(required=True, default='test@test.de')
        field.validate()
        self.assertEqual(field.to_python(), 'test@test.de')
        self.assertEqual(field.to_native(), 'test@test.de')

        field = EmailField(required=True, default='test')
        self.assertRaises(SerializerFieldValueError, field.validate)

        field = EmailField(required=False, on_null=HIDE_FIELD)
        self.assertRaises(IgnoreField, field.to_native)
        self.assertIsNone(field.to_python())

    def test_choice_field(self):
        choices = ('one', 'two', 'three',)
        field = ChoiceField(required=True, choices=choices)
        field.set_value('one')
        field.validate()
        self.assertEqual(field.to_python(), 'one')
        self.assertEqual(field.to_native(), 'one')

        choices = (
            (1, 'one'),
            (2, 'two'),
            (3, 'three'),
        )
        field = ChoiceField(required=True, choices=choices)
        field.set_value('two')
        field.validate()
        self.assertEqual(field.to_python(), 2)
        self.assertEqual(field.to_native(), 'two')

        field = ChoiceField(required=True, choices=choices)
        field.set_value('four')
        self.assertRaises(SerializerFieldValueError, field.validate)

        field = ChoiceField(required=True, choices=choices, default='three')
        field.validate()
        self.assertEqual(field.to_python(), 3)
        self.assertEqual(field.to_native(), 'three')

    def test_boolean_field(self):
        field = BooleanField(required=True)
        field.set_value(False)
        field.validate()
        self.assertEqual(field.to_python(), False)
        self.assertEqual(field.to_native(), False)

        field = BooleanField(required=True, default=True)
        field.validate()
        self.assertEqual(field.to_python(), True)
        self.assertEqual(field.to_native(), True)

        field = BooleanField(required=True)
        self.assertRaises(SerializerFieldValueError, field.validate)

        field = BooleanField(required=False, on_null=HIDE_FIELD)
        self.assertRaises(IgnoreField, field.to_native)
        self.assertIsNone(field.to_python())

    def test_list_field(self):
        uuids = [
            '0203a23f-032c-46be-a1fa-c85fd0284b4c',
            'd2e6a469-a4fd-415e-8c22-b8d73856a714',
            '8832f5cd-c024-49ce-b27a-8d6e388f3b08'
        ]
        field = ListField(UUIDField, required=True)
        field.set_value(value=uuids)
        field.validate()
        self.assertIn('0203a23f-032c-46be-a1fa-c85fd0284b4c', field.to_native())
        self.assertIn('d2e6a469-a4fd-415e-8c22-b8d73856a714', field.to_native())
        self.assertIn('8832f5cd-c024-49ce-b27a-8d6e388f3b08', field.to_native())
        self.assertIn(uuid.UUID('0203a23f-032c-46be-a1fa-c85fd0284b4c'), field.to_python())
        self.assertIn(uuid.UUID('d2e6a469-a4fd-415e-8c22-b8d73856a714'), field.to_python())
        self.assertIn(uuid.UUID('8832f5cd-c024-49ce-b27a-8d6e388f3b08'), field.to_python())
        self.assertEqual(len(field), 3)
        self.assertEqual(uuid.UUID('0203a23f-032c-46be-a1fa-c85fd0284b4c'), field[0])
        self.assertEqual(uuid.UUID('d2e6a469-a4fd-415e-8c22-b8d73856a714'), field[1])
        self.assertEqual(uuid.UUID('8832f5cd-c024-49ce-b27a-8d6e388f3b08'), field[2])

        uuids = [
            '1203a23f-032c-46be-a1fa-c85fd0284b4c',
            '22e6a469-a4fd-415e-8c22-b8d73856a714',
            'no_uuid_value'
        ]
        field = ListField(UUIDField, required=True)
        field.set_value(value=uuids)
        self.assertRaises(SerializerFieldValueError, field.validate)
        field[2] = '3832f5cd-c024-49ce-b27a-8d6e388f3b08'
        field.validate()
        self.assertEqual(len(field), 3)
        self.assertEqual(uuid.UUID('1203a23f-032c-46be-a1fa-c85fd0284b4c'), field[0])
        self.assertEqual(uuid.UUID('22e6a469-a4fd-415e-8c22-b8d73856a714'), field[1])
        self.assertEqual(uuid.UUID('3832f5cd-c024-49ce-b27a-8d6e388f3b08'), field[2])
        field.append(uuid.UUID('4832f5cd-c024-49ce-b27a-8d6e388f3b08'))
        self.assertEqual(len(field), 4)

        emails = [
            'foobar0@test.de',
            'foobar1@test.de',
            'foobar2@test.de',
            'foobar3@test.de'
        ]
        field = ListField(EmailField, required=True)
        field.set_value(value=emails)
        field.validate()
        self.assertIn('foobar0@test.de', field.to_native())
        self.assertIn('foobar0@test.de', field.to_python())
        self.assertEqual(len(field), 4)
        self.assertEqual('foobar0@test.de', field[0])
        self.assertEqual('foobar1@test.de', field[1])
        self.assertEqual('foobar2@test.de', field[2])
        self.assertEqual('foobar3@test.de', field[3])

        field = ListField(EmailField, required=True)
        field.set_value(value=['no_email'])
        self.assertRaises(SerializerFieldValueError, field.validate)


if __name__ == '__main__':
    unittest.main()