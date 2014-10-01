# -*- coding: utf-8 -*-

import unittest
import uuid
import decimal
from datetime import datetime, date, time
from aserializer.utils import py2to3
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
                                ListField,
                                ListSerializerField,)
from aserializer import Serializer


class TypeFieldTests(unittest.TestCase):

    def test_set_value(self):
        type_field = TypeField('first_type')
        type_field.set_value('second_type')
        type_field.validate()
        self.assertEqual(type_field.to_python(), 'second_type')
        self.assertEqual(type_field.to_native(), 'second_type')

    def test_fixed(self):
        type_field = TypeField('first_type', fixed=True)
        type_field.set_value('second_type')
        type_field.validate()
        self.assertEqual(type_field.to_python(), 'first_type')
        self.assertEqual(type_field.to_native(), 'first_type')

    def test_validate(self):
        type_field = TypeField('first_type', validate=True)
        type_field.set_value('second_type')
        self.assertRaises(SerializerFieldValueError, type_field.validate)
        try:
            type_field.validate()
        except SerializerFieldValueError as e:
            self.assertEqual(e.errors, 'Value is not first_type.')

    def test_fixed_validate(self):
        type_field = TypeField('first_type', fixed=True, validate=True)
        type_field.set_value('second_type')
        type_field.validate()
        self.assertEqual(type_field.to_python(), 'first_type')
        self.assertEqual(type_field.to_native(), 'first_type')


class IntegerFieldTests(unittest.TestCase):

    def test_set_value_int(self):
        int_field = IntegerField(required=True)
        int_field.set_value(23)
        int_field.validate()
        self.assertEqual(int_field.to_python(), 23)
        self.assertEqual(int_field.to_native(), 23)

    def test_set_value_string(self):
        int_field = IntegerField(required=True)
        int_field.set_value('24')
        int_field.validate()
        self.assertEqual(int_field.to_python(), 24)
        self.assertEqual(int_field.to_native(), 24)

    def test_validate_raises(self):
        int_field = IntegerField(required=True)
        int_field.set_value('int')
        self.assertRaises(SerializerFieldValueError, int_field.validate)

    def test_max_min(self):
        int_field = IntegerField(required=True, max_value=24, min_value=22)
        int_field.set_value(23)
        int_field.validate()
        self.assertEqual(int_field.to_python(), 23)
        self.assertEqual(int_field.to_native(), 23)

        int_field = IntegerField(required=True, max_value=24, min_value=22)
        int_field.set_value(100)
        self.assertRaises(SerializerFieldValueError, int_field.validate)

    def test_default(self):
        int_field = IntegerField(required=True, max_value=24, min_value=22, default=23)
        self.assertEqual(int_field.to_python(), 23)
        self.assertEqual(int_field.to_native(), 23)

    def test_hide_on_null(self):
        int_field = IntegerField(required=False, on_null=HIDE_FIELD)
        self.assertRaises(IgnoreField, int_field.to_native)
        self.assertIsNone(int_field.to_python())


class FloatFieldTests(unittest.TestCase):

    def test_set_value(self):
        float_field = FloatField(required=True)
        float_field.set_value(23.23)
        float_field.validate()
        self.assertEqual(float_field.to_python(), 23.23)
        self.assertEqual(float_field.to_native(), 23.23)

    def test_set_value_string(self):
        float_field = FloatField(required=True)
        float_field.set_value('24.24')
        float_field.validate()
        self.assertEqual(float_field.to_python(), 24.24)
        self.assertEqual(float_field.to_native(), 24.24)

    def test_validate_raises(self):
        float_field = FloatField(required=True)
        float_field.set_value('float')
        self.assertRaises(SerializerFieldValueError, float_field.validate)

    def test_max_min(self):
        float_field = FloatField(required=True, max_value=24.5, min_value=22.1)
        float_field.set_value(24.6)
        self.assertRaises(SerializerFieldValueError, float_field.validate)

        float_field = FloatField(required=True, max_value=24.5, min_value=22.1)
        float_field.set_value(21.6)
        self.assertRaises(SerializerFieldValueError, float_field.validate)

    def test_default(self):
        float_field = FloatField(required=True, default=23.23)
        float_field.validate()
        self.assertEqual(float_field.to_python(), 23.23)
        self.assertEqual(float_field.to_native(), 23.23)

    def test_hide_on_null(self):
        float_field = FloatField(required=False, on_null=HIDE_FIELD)
        self.assertRaises(IgnoreField, float_field.to_native)
        self.assertIsNone(float_field.to_python())


class DecimalFieldTests(unittest.TestCase):

    def test_set_value(self):
        field = DecimalField(required=True, decimal_places=2)
        field.set_value(23.23)
        field.validate()
        self.assertEqual(field.to_python(), decimal.Decimal('23.23'))
        self.assertEqual(field.to_native(), 23.23)

    def test_set_value_string(self):
        field = DecimalField(required=True, decimal_places=2)
        field.set_value('23.23')
        field.validate()
        self.assertEqual(field.to_python(), decimal.Decimal('23.23'))
        self.assertEqual(field.to_native(), 23.23)

    def test_validate_raises(self):
        field = DecimalField(required=True)
        field.set_value('float')
        self.assertRaises(SerializerFieldValueError, field.validate)

    def test_decimal_places(self):
        field = DecimalField(required=True, decimal_places=1, max_value=24.5, min_value=22.1)
        field.set_value(23.4)
        field.validate()
        self.assertEqual(field, 23.4)
        self.assertEqual(field.to_python(), decimal.Decimal('23.4'))
        self.assertEqual(field.to_native(), 23.4)

        field = DecimalField(required=True, decimal_places=5)
        field.set_value(decimal.Decimal('9.4'))
        field.validate()
        self.assertEqual(field.to_python(), decimal.Decimal('9.40000'))
        self.assertEqual(field.to_native(), 9.40000)

    def test_string_output(self):
        field = DecimalField(required=True, decimal_places=2, output=DecimalField.OUTPUT_AS_STRING)
        field.set_value(23.42)
        field.validate()
        self.assertEqual(field, '23.42')
        self.assertEqual(field.to_python(), decimal.Decimal('23.42'))
        self.assertEqual(field.to_native(), '23.42')

    def test_output_fallback(self):
        field = DecimalField(required=True, decimal_places=1, output='no_valid_output')
        field.set_value(23.4)
        field.validate()
        self.assertEqual(field, 23.4)
        self.assertEqual(field.to_python(), decimal.Decimal('23.4'))
        self.assertEqual(field.to_native(), 23.4)

    def test_max_min(self):
        field = DecimalField(required=True, max_value=24.5, min_value=22.1)
        field.set_value(24.6)
        self.assertRaises(SerializerFieldValueError, field.validate)

        field = DecimalField(required=True, max_value=24.5, min_value=22.1)
        field.set_value(21.6)
        self.assertRaises(SerializerFieldValueError, field.validate)

    def test_default(self):
        field = DecimalField(required=True, default=23.23)
        field.validate()
        self.assertEqual(field.to_python(), decimal.Decimal('23.23'))
        self.assertEqual(field.to_native(), 23.23)

        field = DecimalField(required=True, default=decimal.Decimal('123.123'))
        field.validate()
        self.assertEqual(field.to_python(), decimal.Decimal('123.123'))
        self.assertEqual(field.to_native(), 123.123)

    def test_hide_on_null(self):
        field = DecimalField(required=False, on_null=HIDE_FIELD)
        self.assertRaises(IgnoreField, field.to_native)
        self.assertIsNone(field.to_python())


class StringFieldTests(unittest.TestCase):

    def test_set_value(self):
        field = StringField(required=True)
        field.set_value('string')
        field.validate()
        self.assertEqual(field.to_python(), 'string')
        self.assertEqual(field.to_native(), 'string')

    def test_validate_raises(self):
        field = StringField(required=True)
        field.set_value(12)
        self.assertRaises(SerializerFieldValueError, field.validate)

    def test_default(self):
        field = StringField(required=True, default='a string')
        field.validate()
        self.assertEqual(field.to_python(), 'a string')
        self.assertEqual(field.to_native(), 'a string')

    def test_hide_on_null(self):
        field = StringField(required=False, on_null=HIDE_FIELD)
        self.assertRaises(IgnoreField, field.to_native)
        self.assertIsNone(field.to_python())


class UUIDFieldTests(unittest.TestCase):

    def test_set_value(self):
        field = UUIDField(required=True)
        field.set_value(uuid.uuid4())
        field.validate()
        self.assertIsInstance(field.to_python(), uuid.UUID)

    def test_set_value_string(self):
        field = UUIDField(required=True)
        field.set_value('8005ea5e-60b7-4b2a-ab41-a773b8b72e84'.upper())
        field.validate()
        self.assertIsInstance(field.to_python(), uuid.UUID)
        self.assertEqual(field.to_python(),  uuid.UUID('8005ea5e-60b7-4b2a-ab41-a773b8b72e84'))
        self.assertEqual(field.to_native(), '8005ea5e-60b7-4b2a-ab41-a773b8b72e84'.upper())

    def test_no_binary(self):
        field = UUIDField(required=True, binary=False)
        field.set_value('8005ea5e-60b7-4b2a-ab41-a773b8b72e84'.upper())
        field.validate()
        self.assertIsInstance(field.to_python(), py2to3.string)
        self.assertEqual(field.to_python(), '8005ea5e-60b7-4b2a-ab41-a773b8b72e84')
        self.assertEqual(field.to_native(), '8005ea5e-60b7-4b2a-ab41-a773b8b72e84'.upper())

    def test_validate_raises(self):
        field = UUIDField(required=True)
        field.set_value('nono')
        self.assertRaises(SerializerFieldValueError, field.validate)

    def test_required(self):
        field = UUIDField(required=True)
        self.assertRaises(SerializerFieldValueError, field.validate)

        field = UUIDField(required=False)
        field.validate()
        self.assertIsNone(field.to_python())
        self.assertEqual(field.to_native(), '')

    def test_default(self):
        field = UUIDField(required=True, default=uuid.UUID('8005ea5e-60b7-4b2a-ab41-a773b8b72e84'))
        field.validate()
        self.assertEqual(field.to_python(),  uuid.UUID('8005ea5e-60b7-4b2a-ab41-a773b8b72e84'))
        self.assertEqual(field.to_native(), '8005ea5e-60b7-4b2a-ab41-a773b8b72e84'.upper())

        field = UUIDField(required=True, default='8005ea5e-60b7-4b2a-ab41-a773b8b72e84')
        field.validate()
        self.assertEqual(field.to_python(),  uuid.UUID('8005ea5e-60b7-4b2a-ab41-a773b8b72e84'))
        self.assertEqual(field.to_native(), '8005ea5e-60b7-4b2a-ab41-a773b8b72e84'.upper())

    def test_hide_on_null(self):
        field = UUIDField(required=False, on_null=HIDE_FIELD)
        self.assertRaises(IgnoreField, field.to_native)
        self.assertIsNone(field.to_python())


class DatetimeFieldTests(unittest.TestCase):

    def test_set_value(self):
        dt = datetime.strptime('2013-10-07T22:58:40', '%Y-%m-%dT%H:%M:%S')
        field = DatetimeField(required=True)
        field.set_value(dt)
        field.validate()
        self.assertIsInstance(field.to_python(), datetime)
        self.assertEqual(field.to_python(), dt)
        self.assertEqual(field.to_native(), '2013-10-07T22:58:40')

    def test_set_value_string(self):
        field = DatetimeField(required=True)
        field.set_value('2013-10-07T20:15:23')
        field.validate()
        self.assertEqual(field.to_python(), datetime.strptime('2013-10-07T20:15:23', '%Y-%m-%dT%H:%M:%S'))
        self.assertEqual(field.to_native(), '2013-10-07T20:15:23')

    def test_formats(self):
        field = DatetimeField(required=True, formats=['%d.%m.%Y %H:%M:%S'])
        field.set_value('07.10.2013 20:15:23')
        field.validate()
        self.assertEqual(field.to_python(), datetime.strptime('2013-10-07T20:15:23', '%Y-%m-%dT%H:%M:%S'))
        self.assertEqual(field.to_native(), '07.10.2013 20:15:23')

    def test_serialize_to(self):
        field = DatetimeField(required=True, formats=['%d.%m.%Y %H:%M:%S'], serialize_to='%Y-%m-%dT%H:%M:%S.%f')
        field.set_value('07.10.2013 20:15:23')
        field.validate()
        self.assertEqual(field.to_python(), datetime.strptime('2013-10-07T20:15:23', '%Y-%m-%dT%H:%M:%S'))
        self.assertEqual(field.to_native(), '2013-10-07T20:15:23.000000')

    def test_validate_raises(self):
        field = DatetimeField(required=True)
        field.set_value('datetime')
        self.assertRaises(SerializerFieldValueError, field.validate)

    def test_default(self):
        dt = datetime.strptime('2013-10-07T22:58:40', '%Y-%m-%dT%H:%M:%S')
        field = DatetimeField(required=True, default=dt)
        field.validate()
        self.assertEqual(field.to_python(), dt)
        self.assertEqual(field.to_native(), '2013-10-07T22:58:40')

        field = DatetimeField(required=True, default='2013-10-07T22:58:40')
        field.validate()
        self.assertEqual(field.to_python(), dt)
        self.assertEqual(field.to_native(), '2013-10-07T22:58:40')

    def test_hide_on_null(self):
        field = DatetimeField(required=False, on_null=HIDE_FIELD)
        self.assertRaises(IgnoreField, field.to_native)
        self.assertIsNone(field.to_python())


class DateFieldTests(unittest.TestCase):

    def test_set_value(self):
        _date = datetime.strptime('2013-10-07T22:58:40', '%Y-%m-%dT%H:%M:%S').date()
        field = DateField(required=True)
        field.set_value(_date)
        field.validate()
        self.assertIsInstance(field.to_python(), date)
        self.assertEqual(field.to_python(), _date)
        self.assertEqual(field.to_native(), '2013-10-07')

    def test_set_value_string(self):
        field = DateField(required=True)
        field.set_value('2013-10-07')
        field.validate()
        self.assertEqual(field.to_python(), datetime.strptime('2013-10-07T20:15:23', '%Y-%m-%dT%H:%M:%S').date())
        self.assertEqual(field.to_native(), '2013-10-07')

    def test_validate_raises(self):
        field = DateField(required=True)
        field.set_value('date')
        self.assertRaises(SerializerFieldValueError, field.validate)

    def test_default(self):
        field = DateField(required=True, default='2013-10-07')
        field.validate()
        self.assertEqual(field.to_python(), datetime.strptime('2013-10-07T20:15:23', '%Y-%m-%dT%H:%M:%S').date())
        self.assertEqual(field.to_native(), '2013-10-07')

    def test_hide_on_null(self):
        field = DateField(required=False, on_null=HIDE_FIELD)
        self.assertRaises(IgnoreField, field.to_native)
        self.assertIsNone(field.to_python())


class TimeFieldTests(unittest.TestCase):

    def test_set_value(self):
        t = datetime.strptime('2013-10-07T22:58:40', '%Y-%m-%dT%H:%M:%S').time()
        field = TimeField(required=True)
        field.set_value(t)
        field.validate()
        self.assertIsInstance(field.to_python(), time)
        self.assertEqual(field.to_python(), t)
        self.assertEqual(field.to_native(), '22:58:40')

    def test_set_value_string(self):
        field = TimeField(required=True)
        field.set_value('22:00:40')
        field.validate()
        self.assertEqual(field.to_python(), datetime.strptime('2013-10-07T22:00:40', '%Y-%m-%dT%H:%M:%S').time())
        self.assertEqual(field.to_native(), '22:00:40')

    def test_validate_raises(self):
        field = TimeField(required=True)
        field.set_value('time')
        self.assertRaises(SerializerFieldValueError, field.validate)

    def test_default(self):
        t = datetime.strptime('2013-10-07T22:58:40', '%Y-%m-%dT%H:%M:%S').time()
        field = TimeField(required=True, default=t)
        field.validate()
        self.assertEqual(field.to_python(), t)
        self.assertEqual(field.to_native(), '22:58:40')

        field = TimeField(required=True, default='22:58:40')
        field.validate()
        self.assertEqual(field.to_python(), t)
        self.assertEqual(field.to_native(), '22:58:40')

    def test_hide_on_null(self):
        field = TimeField(required=False, on_null=HIDE_FIELD)
        self.assertRaises(IgnoreField, field.to_native)
        self.assertIsNone(field.to_python())


class UrlFieldTests(unittest.TestCase):

    def test_set_value(self):
        field = UrlField(required=True)
        field.set_value('https://www.onyg.de')
        field.validate()
        self.assertEqual(field.to_python(), 'https://www.onyg.de')
        self.assertEqual(field.to_native(), 'https://www.onyg.de')

    def test_base(self):
        field = UrlField(required=True, base='http://www.onyg.de')
        field.set_value('api')
        field.validate()
        self.assertEqual(field.to_python(), 'http://www.onyg.de/api')
        self.assertEqual(field.to_native(), 'http://www.onyg.de/api')

    def test_validate_raises(self):
        field = UrlField(required=True)
        field.set_value('api')
        self.assertRaises(SerializerFieldValueError, field.validate)

    def test_default(self):
        field = UrlField(required=True, default='https://www.onyg.de')
        field.validate()
        self.assertEqual(field.to_python(), 'https://www.onyg.de')
        self.assertEqual(field.to_native(), 'https://www.onyg.de')

        field = UrlField(required=True, default='no url')
        self.assertRaises(SerializerFieldValueError, field.validate)

    def test_hide_on_null(self):
        field = UrlField(required=False, on_null=HIDE_FIELD)
        self.assertRaises(IgnoreField, field.to_native)
        self.assertIsNone(field.to_python())


class EmailFieldTests(unittest.TestCase):

    def test_set_value(self):
        field = EmailField(required=True)
        field.set_value('test@test.de')
        field.validate()
        self.assertEqual(field.to_python(), 'test@test.de')
        self.assertEqual(field.to_native(), 'test@test.de')

    def test_validate_raises(self):
        field = EmailField(required=True, default='test')
        self.assertRaises(SerializerFieldValueError, field.validate)

        field = EmailField(required=True)
        field.set_value('test.test.de')
        self.assertRaises(SerializerFieldValueError, field.validate)

    def test_default(self):
        field = EmailField(required=True, default='test@test.de')
        field.validate()
        self.assertEqual(field.to_python(), 'test@test.de')
        self.assertEqual(field.to_native(), 'test@test.de')

    def test_hide_on_null(self):
        field = EmailField(required=False, on_null=HIDE_FIELD)
        self.assertRaises(IgnoreField, field.to_native)
        self.assertIsNone(field.to_python())


class ChoiceFieldTests(unittest.TestCase):
    LIST_CHOICES =  ('one', 'two', 'three',)
    TUPLE_CHOICES = (
        (1, 'one'),
        (2, 'two'),
        (3, 'three'),
    )

    def test_choices_list(self):
        field = ChoiceField(required=True, choices=self.LIST_CHOICES)
        field.set_value('one')
        field.validate()
        self.assertEqual(field.to_python(), 'one')
        self.assertEqual(field.to_native(), 'one')

    def test_choices_tuple(self):
        field = ChoiceField(required=True, choices=self.TUPLE_CHOICES)
        field.set_value('two')
        field.validate()
        self.assertEqual(field.to_python(), 2)
        self.assertEqual(field.to_native(), 'two')

        field = ChoiceField(required=True, choices=self.TUPLE_CHOICES)
        field.set_value(2)
        self.assertRaises(SerializerFieldValueError, field.validate)

    def test_validate_raises(self):
        field = ChoiceField(required=True, choices=self.TUPLE_CHOICES)
        field.set_value('four')
        self.assertRaises(SerializerFieldValueError, field.validate)

    def test_default(self):
        field = ChoiceField(required=True, choices=self.TUPLE_CHOICES, default='three')
        field.validate()
        self.assertEqual(field.to_python(), 3)
        self.assertEqual(field.to_native(), 'three')

    def test_default_no_validate(self):
        field = ChoiceField(required=True, choices=self.TUPLE_CHOICES, default='three')
        self.assertEqual(field.to_python(), 3)
        self.assertEqual(field.to_native(), 'three')


class BooleanFieldTests(unittest.TestCase):

    def test_set_value(self):
        field = BooleanField(required=True)
        field.set_value(False)
        field.validate()
        self.assertEqual(field.to_python(), False)
        self.assertEqual(field.to_native(), False)

    def test_default(self):
        field = BooleanField(required=True, default=True)
        field.validate()
        self.assertEqual(field.to_python(), True)
        self.assertEqual(field.to_native(), True)

        field = BooleanField(required=True, default=False)
        field.validate()
        self.assertEqual(field.to_python(), False)
        self.assertEqual(field.to_native(), False)

    def test_validate_raises(self):
        field = BooleanField(required=True)
        self.assertRaises(SerializerFieldValueError, field.validate)

    def test_hide_on_null(self):
        field = BooleanField(required=False, on_null=HIDE_FIELD)
        self.assertRaises(IgnoreField, field.to_native)
        self.assertIsNone(field.to_python())


class ListFieldUUIDFieldTests(unittest.TestCase):

    def test_set_value(self):
        uuids = [
            '0203a23f-032c-46be-a1fa-c85fd0284b4c',
            'd2e6a469-a4fd-415e-8c22-b8d73856a714',
            '8832f5cd-c024-49ce-b27a-8d6e388f3b08'
        ]
        field = ListField(UUIDField, required=True)
        field.set_value(value=uuids)
        field.validate()
        self.assertIn('0203a23f-032c-46be-a1fa-c85fd0284b4c'.upper(), field.to_native())
        self.assertIn('d2e6a469-a4fd-415e-8c22-b8d73856a714'.upper(), field.to_native())
        self.assertIn('8832f5cd-c024-49ce-b27a-8d6e388f3b08'.upper(), field.to_native())
        self.assertIn(uuid.UUID('0203a23f-032c-46be-a1fa-c85fd0284b4c'), field.to_python())
        self.assertIn(uuid.UUID('d2e6a469-a4fd-415e-8c22-b8d73856a714'), field.to_python())
        self.assertIn(uuid.UUID('8832f5cd-c024-49ce-b27a-8d6e388f3b08'), field.to_python())
        self.assertEqual(len(field), 3)
        self.assertEqual(uuid.UUID('0203a23f-032c-46be-a1fa-c85fd0284b4c'), field[0])
        self.assertEqual(uuid.UUID('d2e6a469-a4fd-415e-8c22-b8d73856a714'), field[1])
        self.assertEqual(uuid.UUID('8832f5cd-c024-49ce-b27a-8d6e388f3b08'), field[2])

    def test_validate_raises(self):
        uuids = [
            '1203a23f-032c-46be-a1fa-c85fd0284b4c',
            '22e6a469-a4fd-415e-8c22-b8d73856a714',
            'no_uuid_value'
        ]
        field = ListField(UUIDField, required=True)
        field.set_value(value=uuids)
        self.assertRaises(SerializerFieldValueError, field.validate)

    def test_set_list_index(self):
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

    def test_append(self):
        uuids = [
            '1203a23f-032c-46be-a1fa-c85fd0284b4c',
        ]
        field = ListField(UUIDField, required=True)
        field.set_value(value=uuids)
        self.assertEqual(len(field), 1)
        field.append(uuid.UUID('4832f5cd-c024-49ce-b27a-8d6e388f3b08'))
        self.assertEqual(len(field), 2)
        field.validate()
        self.assertEqual(uuid.UUID('1203a23f-032c-46be-a1fa-c85fd0284b4c'), field[0])
        self.assertEqual(uuid.UUID('4832f5cd-c024-49ce-b27a-8d6e388f3b08'), field[1])


class ListFieldEmailFieldTests(unittest.TestCase):

    def test_set_value(self):
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
        for email in field:
            self.assertIn(email, emails)

    def test_validate_raises(self):
        field = ListField(EmailField, required=True)
        field.set_value(value=['no_email'])
        self.assertRaises(SerializerFieldValueError, field.validate)

        field = ListField(EmailField, required=True)
        self.assertRaises(SerializerFieldValueError, field.validate)


class ListSerializerFieldTests(unittest.TestCase):

    class TestSerializer(Serializer):
        uuid = UUIDField(required=True)
        name = StringField(required=True)
        foo_number = IntegerField(required=False)

    class TestObject(object):
        def __init__(self, uuid, name, foo_number):
            self.uuid = uuid
            self.name = name
            self.foo_number = foo_number

        def get(self, key):
            return getattr(self, key)

    def _test_objects(self, uuids):
        objects = [
            dict(uuid=uuids[0], name='ONE', foo_number=1),
            dict(uuid=uuids[1], name='TWO', foo_number=2),
            self.TestObject(uuid=uuids[2], name='THREE', foo_number=3)
        ]
        return objects

    def test_set_value(self):
        uuids = [
            '0203a23f-032c-46be-a1fa-c85fd0284b4c',
            'd2e6a469-a4fd-415e-8c22-b8d73856a714',
            '8832f5cd-c024-49ce-b27a-8d6e388f3b08'
        ]
        objects = self._test_objects(uuids)
        field = ListSerializerField(self.TestSerializer, required=True)

        field.set_value(value=objects)
        field.validate()
        for value in field.to_python():
            self.assertIn(str(value.get('uuid')), uuids)
            self.assertIn(str(value.get('name')), ['ONE', 'TWO', 'THREE'])

    def test_validate_raises(self):
        uuids = [
            '1203a23f-032c-46be-a1fa-c85fd0284b4c',
            '22e6a469-a4fd-415e-8c22-b8d73856a714',
            'no_uuid_value'
        ]
        objects = self._test_objects(uuids)
        field = ListSerializerField(self.TestSerializer, required=True)
        field.set_value(value=objects)
        self.assertRaises(SerializerFieldValueError, field.validate)


class SerializerFieldValueErrorTests(unittest.TestCase):

    def test_required(self):
        field = IntegerField(required=True)
        try:
            field.validate()
        except SerializerFieldValueError as e:
            self.assertEqual(repr(e), 'This field is required.')
            self.assertEqual(str(e), '[field]: This field is required.')
        else:
            self.fail('SerializerFieldValueError not raised.')

    def test_invalid(self):
        field = UUIDField(required=True)
        field.set_value('no_uuid')
        try:
            field.validate()
        except SerializerFieldValueError as e:
            self.assertEqual(repr(e), 'Invalid value.')
            self.assertEqual(str(e), '[field]: Invalid value.')
        else:
            self.fail('SerializerFieldValueError not raised.')


if __name__ == '__main__':
    unittest.main()