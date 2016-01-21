# -*- coding: utf-8 -*-

import unittest
from aserializer import fields
from aserializer.django.serializers import DjangoModelSerializerBase
from tests.django_tests import django, SKIPTEST_TEXT, TestCase, SKIPTEST_TEXT_VERSION_18

if django is not None:
    from tests.django_tests.django_app.models import SimpleModelForSerializer, UUIDFieldModel


@unittest.skipIf(django is None, SKIPTEST_TEXT)
class ModelSerializerFieldMappingTests(TestCase):

    def test_char_field(self):
        model_field = SimpleModelForSerializer._meta.get_field('char_field')
        serializer_field = DjangoModelSerializerBase.get_field_from_modelfield(model_field)
        self.assertIsInstance(serializer_field, fields.StringField)

    def test_integer_field(self):
        model_field = SimpleModelForSerializer._meta.get_field('integer_field')
        serializer_field = DjangoModelSerializerBase.get_field_from_modelfield(model_field)
        self.assertIsInstance(serializer_field, fields.IntegerField)

    def test_positiveinteger_field(self):
        model_field = SimpleModelForSerializer._meta.get_field('positiveinteger_field')
        serializer_field = DjangoModelSerializerBase.get_field_from_modelfield(model_field)
        self.assertIsInstance(serializer_field, fields.PositiveIntegerField)

    def test_float_field(self):
        model_field = SimpleModelForSerializer._meta.get_field('float_field')
        serializer_field = DjangoModelSerializerBase.get_field_from_modelfield(model_field)
        self.assertIsInstance(serializer_field, fields.FloatField)

    def test_date_field(self):
        model_field = SimpleModelForSerializer._meta.get_field('date_field')
        serializer_field = DjangoModelSerializerBase.get_field_from_modelfield(model_field)
        self.assertIsInstance(serializer_field, fields.DateField)

    def test_datetime_field(self):
        model_field = SimpleModelForSerializer._meta.get_field('datetime_field')
        serializer_field = DjangoModelSerializerBase.get_field_from_modelfield(model_field)
        self.assertIsInstance(serializer_field, fields.DatetimeField)

    def test_time_field(self):
        model_field = SimpleModelForSerializer._meta.get_field('time_field')
        serializer_field = DjangoModelSerializerBase.get_field_from_modelfield(model_field)
        self.assertIsInstance(serializer_field, fields.TimeField)

    def test_boolean_field(self):
        model_field = SimpleModelForSerializer._meta.get_field('boolean_field')
        serializer_field = DjangoModelSerializerBase.get_field_from_modelfield(model_field)
        self.assertIsInstance(serializer_field, fields.BooleanField)

    def test_decimal_field(self):
        model_field = SimpleModelForSerializer._meta.get_field('decimal_field')
        serializer_field = DjangoModelSerializerBase.get_field_from_modelfield(model_field)
        self.assertIsInstance(serializer_field, fields.DecimalField)

    def test_text_field(self):
        model_field = SimpleModelForSerializer._meta.get_field('text_field')
        serializer_field = DjangoModelSerializerBase.get_field_from_modelfield(model_field)
        self.assertIsInstance(serializer_field, fields.StringField)

    def test_commaseparatedinteger_field(self):
        model_field = SimpleModelForSerializer._meta.get_field('commaseparatedinteger_field')
        serializer_field = DjangoModelSerializerBase.get_field_from_modelfield(model_field)
        self.assertIsInstance(serializer_field, fields.StringField)

    def test_choice_field(self):
        model_field = SimpleModelForSerializer._meta.get_field('choice_field')
        serializer_field = DjangoModelSerializerBase.get_field_from_modelfield(model_field)
        self.assertIsInstance(serializer_field, fields.ChoiceField)
        self.assertEqual(list(serializer_field.choices), list(model_field.choices))

    def test_url_field(self):
        model_field = SimpleModelForSerializer._meta.get_field('url_field')
        serializer_field = DjangoModelSerializerBase.get_field_from_modelfield(model_field)
        self.assertIsInstance(serializer_field, fields.UrlField)

    @unittest.skipIf(django is None or django.VERSION < (1, 8, 0), SKIPTEST_TEXT_VERSION_18)
    def test_uuid_field(self):
        model_field = UUIDFieldModel._meta.get_field('uuid_field')
        serializer_field = DjangoModelSerializerBase.get_field_from_modelfield(model_field)
        self.assertIsInstance(serializer_field, fields.UUIDField)