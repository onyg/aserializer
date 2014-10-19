# -*- coding: utf-8 -*-

import os
import unittest
from datetime import datetime
from decimal import Decimal

from aserializer import Serializer
from aserializer import fields
from aserializer.django.fields import RelatedManagerListSerializerField
from aserializer.django.collection import DjangoCollectionSerializer
from aserializer.django.serializers import DjangoModelSerializer, DjangoModelSerializerBase

try:
    import django
except ImportError:
    django = None


SKIPTEST_TEXT = "Django is not installed."
DJANGO_RUNNER = None
DJANGO_RUNNER_STATE = None


if django is not None:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.django_app.settings')
    from django.test import TestCase
    from django.test.runner import DiscoverRunner
    from django.test.utils import setup_test_environment
    if django.VERSION >= (1, 7, 0):
        django.setup()
    from tests.django_app.models import (
        SimpleDjangoModel,
        RelatedDjangoModel,
        SimpleModelForSerializer,
    )
else:
    from unittest import TestCase



def setUpModule():
    if django is None:
        raise unittest.SkipTest(SKIPTEST_TEXT)
    setup_test_environment()
    global DJANGO_RUNNER
    global DJANGO_RUNNER_STATE
    DJANGO_RUNNER = DiscoverRunner()
    DJANGO_RUNNER_STATE = DJANGO_RUNNER.setup_databases()


def tearDownModule():
    if django is None:
        return
    global DJANGO_RUNNER
    global DJANGO_RUNNER_STATE
    if DJANGO_RUNNER and DJANGO_RUNNER_STATE:
        DJANGO_RUNNER.teardown_databases(DJANGO_RUNNER_STATE)


class SimpleDjangoModelSerializer(Serializer):
    name = fields.StringField(required=True, max_length=24)
    code = fields.StringField(max_length=4)
    number = fields.IntegerField(required=True)


class RelatedDjangoModelSerializer(Serializer):
    name = fields.StringField(required=True, max_length=24)
    relation = fields.SerializerField(SimpleDjangoModelSerializer)


class SecondSimpleDjangoModelSerializer(Serializer):
    name = fields.StringField(required=True, max_length=24)
    code = fields.StringField(max_length=4)
    number = fields.IntegerField(required=True)
    relations = RelatedManagerListSerializerField(RelatedDjangoModelSerializer, exclude=['relation'])


@unittest.skipIf(django is None, SKIPTEST_TEXT)
class DjangoSerializerTests(TestCase):

    def tearDown(self):
        SimpleDjangoModel.objects.all().delete()
        RelatedDjangoModel.objects.all().delete()

    def test_serialize(self):
        sdm = SimpleDjangoModel.objects.create(name='The Name', code='AAAA', number=1)

        serializer = SimpleDjangoModelSerializer(sdm)
        self.assertTrue(serializer.is_valid())
        self.assertDictEqual(serializer.dump(), dict(name='The Name', code='AAAA', number=1))

    def test_relation(self):
        sdm = SimpleDjangoModel.objects.create(name='The Name', code='AAAA', number=1)
        rdm = RelatedDjangoModel.objects.create(name='Relation', relation=sdm)

        serializer = RelatedDjangoModelSerializer(rdm)
        self.assertTrue(serializer.is_valid())
        test_value = {
            'name': 'Relation',
            'relation': {
                'name': 'The Name',
                'code': 'AAAA',
                'number': 1
            }
        }
        self.assertDictEqual(serializer.dump(), test_value)

    def test_relation_list(self):
        sdm = SimpleDjangoModel.objects.create(name='The Name', code='AAAA', number=1)
        RelatedDjangoModel.objects.create(name='Relation 1', relation=sdm)
        RelatedDjangoModel.objects.create(name='Relation 2', relation=sdm)
        RelatedDjangoModel.objects.create(name='Relation 3', relation=sdm)

        serializer = SecondSimpleDjangoModelSerializer(sdm)
        self.assertTrue(serializer.is_valid())
        test_value = {
            'name': 'The Name',
            'number': 1,
            'code': 'AAAA',
            'relations': [
                {
                    'name': 'Relation 1'
                },
                {
                    'name': 'Relation 2'
                },
                {
                    'name': 'Relation 3'
                }
            ]
        }
        self.assertDictEqual(serializer.dump(), test_value)


class SimpleDjangoModelCollection(DjangoCollectionSerializer):
    class Meta:
        serializer = SimpleDjangoModelSerializer


@unittest.skipIf(django is None, SKIPTEST_TEXT)
class DjangoCollectionSerializerTests(TestCase):

    def setUp(self):
        SimpleDjangoModel.objects.create(name='One', code='DDDD', number=1)
        SimpleDjangoModel.objects.create(name='One', code='FFFF', number=1)
        SimpleDjangoModel.objects.create(name='Two', code='CCCC', number=2)
        SimpleDjangoModel.objects.create(name='Three', code='BBBB', number=3)
        SimpleDjangoModel.objects.create(name='Four', code='AAAA', number=4)

    def tearDown(self):
        SimpleDjangoModel.objects.all().delete()
        RelatedDjangoModel.objects.all().delete()

    def test_simple(self):
        qs = SimpleDjangoModel.objects.all()

        collection = SimpleDjangoModelCollection(qs)
        test_value = {
            "_metadata": {
                "totalCount": 5,
                "offset": 0,
                "limit": 10
            },
            "items": [
                {
                    "name": "One",
                    "code": "DDDD",
                    "number": 1
                },
                {
                    "name": "One",
                    "code": "FFFF",
                    "number": 1
                },
                {
                    "name": "Two",
                    "code": "CCCC",
                    "number": 2
                },
                {
                    "name": "Three",
                    "code": "BBBB",
                    "number": 3
                },
                {
                    "name": "Four",
                    "code": "AAAA",
                    "number": 4
                }
            ]
        }
        self.assertDictEqual(collection.dump(), test_value)

    def test_limit_offset(self):
        qs = SimpleDjangoModel.objects.all()

        collection = SimpleDjangoModelCollection(qs, limit=2, offset=2)
        test_value = {
            "_metadata": {
                "totalCount": 5,
                "offset": 2,
                "limit": 2
            },
            "items": [
                {
                    "name": "Two",
                    "code": "CCCC",
                    "number": 2
                },
                {
                    "name": "Three",
                    "code": "BBBB",
                    "number": 3
                }
            ]
        }
        self.assertDictEqual(collection.dump(), test_value)

    def test_sort(self):
        qs = SimpleDjangoModel.objects.all()

        collection = SimpleDjangoModelCollection(qs, sort=['-number'])
        test_value = {
            "_metadata": {
                "totalCount": 5,
                "offset": 0,
                "limit": 10
            },
            "items": [
                {
                    "name": "Four",
                    "code": "AAAA",
                    "number": 4
                },
                {
                    "name": "Three",
                    "code": "BBBB",
                    "number": 3
                },
                {
                    "name": "Two",
                    "code": "CCCC",
                    "number": 2
                },
                {
                    "name": "One",
                    "code": "DDDD",
                    "number": 1
                },
                {
                    "name": "One",
                    "code": "FFFF",
                    "number": 1
                }
            ]
        }
        self.assertDictEqual(collection.dump(), test_value)

    def test_multiple_sort(self):
        qs = SimpleDjangoModel.objects.all()

        collection = SimpleDjangoModelCollection(qs, limit=2, sort=['number', '-code'])
        test_value = {
            "_metadata": {
                "totalCount": 5,
                "offset": 0,
                "limit": 2
            },
            "items": [
                {
                    "name": "One",
                    "code": "FFFF",
                    "number": 1
                },
                {
                    "name": "One",
                    "code": "DDDD",
                    "number": 1
                }
            ]
        }
        self.assertDictEqual(collection.dump(), test_value)


    def test_multiple_sort_empty_qs(self):
        qs = SimpleDjangoModel.objects.none()

        collection = SimpleDjangoModelCollection(qs, limit=2, sort=['number', '-code'])
        test_value = {
            "_metadata": {
                "totalCount": 0,
                "offset": 0,
                "limit": 2
            },
            "items": []
        }
        self.assertDictEqual(collection.dump(), test_value)

    def test_invalid_sort(self):
        qs = SimpleDjangoModel.objects.all()

        collection = SimpleDjangoModelCollection(qs, sort=['foobar'])
        dump = collection.dump()
        self.assertEqual(dump['items'][0]['code'], 'DDDD')
        self.assertEqual(dump['items'][1]['code'], 'FFFF')
        self.assertEqual(dump['items'][2]['code'], 'CCCC')
        self.assertEqual(dump['items'][3]['code'], 'BBBB')
        self.assertEqual(dump['items'][4]['code'], 'AAAA')

    def test_empty_queryset(self):
        collection = SimpleDjangoModelCollection(SimpleDjangoModel.objects.none())
        test_value = {
            "_metadata": {
                "totalCount": 0,
                "offset": 0,
                "limit": 10
            },
            "items": []
        }
        self.assertDictEqual(collection.dump(), test_value)


class TheDjangoModelSerializer(DjangoModelSerializer):

    class Meta:
        model = SimpleModelForSerializer


class ModelSerializerFieldMappingTests(TestCase):

    def test_char_field(self):
        model_field = SimpleModelForSerializer._meta.get_field_by_name('char_field')[0]
        serializer_field = DjangoModelSerializerBase.get_field_from_modelfield(model_field)
        self.assertIsInstance(serializer_field, fields.StringField)

    def test_integer_field(self):
        model_field = SimpleModelForSerializer._meta.get_field_by_name('integer_field')[0]
        serializer_field = DjangoModelSerializerBase.get_field_from_modelfield(model_field)
        self.assertIsInstance(serializer_field, fields.IntegerField)

    def test_positiveinteger_field(self):
        model_field = SimpleModelForSerializer._meta.get_field_by_name('positiveinteger_field')[0]
        serializer_field = DjangoModelSerializerBase.get_field_from_modelfield(model_field)
        self.assertIsInstance(serializer_field, fields.PositiveIntegerField)

    def test_float_field(self):
        model_field = SimpleModelForSerializer._meta.get_field_by_name('float_field')[0]
        serializer_field = DjangoModelSerializerBase.get_field_from_modelfield(model_field)
        self.assertIsInstance(serializer_field, fields.FloatField)

    def test_date_field(self):
        model_field = SimpleModelForSerializer._meta.get_field_by_name('date_field')[0]
        serializer_field = DjangoModelSerializerBase.get_field_from_modelfield(model_field)
        self.assertIsInstance(serializer_field, fields.DateField)

    def test_datetime_field(self):
        model_field = SimpleModelForSerializer._meta.get_field_by_name('datetime_field')[0]
        serializer_field = DjangoModelSerializerBase.get_field_from_modelfield(model_field)
        self.assertIsInstance(serializer_field, fields.DatetimeField)

    def test_time_field(self):
        model_field = SimpleModelForSerializer._meta.get_field_by_name('time_field')[0]
        serializer_field = DjangoModelSerializerBase.get_field_from_modelfield(model_field)
        self.assertIsInstance(serializer_field, fields.TimeField)

    def test_boolean_field(self):
        model_field = SimpleModelForSerializer._meta.get_field_by_name('boolean_field')[0]
        serializer_field = DjangoModelSerializerBase.get_field_from_modelfield(model_field)
        self.assertIsInstance(serializer_field, fields.BooleanField)

    def test_decimal_field(self):
        model_field = SimpleModelForSerializer._meta.get_field_by_name('decimal_field')[0]
        serializer_field = DjangoModelSerializerBase.get_field_from_modelfield(model_field)
        self.assertIsInstance(serializer_field, fields.DecimalField)

    def test_text_field(self):
        model_field = SimpleModelForSerializer._meta.get_field_by_name('text_field')[0]
        serializer_field = DjangoModelSerializerBase.get_field_from_modelfield(model_field)
        self.assertIsInstance(serializer_field, fields.StringField)

    def test_commaseparatedinteger_field(self):
        model_field = SimpleModelForSerializer._meta.get_field_by_name('commaseparatedinteger_field')[0]
        serializer_field = DjangoModelSerializerBase.get_field_from_modelfield(model_field)
        self.assertIsInstance(serializer_field, fields.StringField)

    def test_choice_field(self):
        model_field = SimpleModelForSerializer._meta.get_field_by_name('choice_field')[0]
        serializer_field = DjangoModelSerializerBase.get_field_from_modelfield(model_field)
        self.assertIsInstance(serializer_field, fields.ChoiceField)
        self.assertEqual(list(serializer_field.choices), list(model_field.choices))

    def test_url_field(self):
        model_field = SimpleModelForSerializer._meta.get_field_by_name('url_field')[0]
        serializer_field = DjangoModelSerializerBase.get_field_from_modelfield(model_field)
        self.assertIsInstance(serializer_field, fields.UrlField)


class FlatSerializerTests(TestCase):
    maxDiff = None

    def tearDown(self):
        SimpleModelForSerializer.objects.all().delete()

    def test_serialize(self):
        values = dict(
            char_field='test',
            integer_field=-23,
            integer_field2=23,
            positiveinteger_field=23,
            float_field=23.23,
            date_field=datetime.strptime('2014-10-07T20:15:23', '%Y-%m-%dT%H:%M:%S').date(),
            datetime_field=datetime.strptime('2014-10-07T20:15:23', '%Y-%m-%dT%H:%M:%S'),
            time_field=datetime.strptime('2014-10-07T20:15:23', '%Y-%m-%dT%H:%M:%S').time(),
            boolean_field=False,
            decimal_field=Decimal('12.12'),
            text_field='test text',
            commaseparatedinteger_field='1,2,3,4',
            choice_field='Zero',
            url_field='http://www.test.test'
        )

        native_values = {
            "float_field": 23.23,
            "url_field": "http://www.test.test",
            "text_field": "test text",
            "time_field": "20:15:23",
            "choice_field": "Zero",
            "char_field": "test",
            "boolean_field": True,
            "integer_field2": 23,
            "commaseparatedinteger_field": "1,2,3,4",
            "id": 1,
            "datetime_field": "2014-10-07T20:15:23",
            "decimal_field": 12.12,
            "date_field": "2014-10-07",
            "integer_field": -23,
            "positiveinteger_field": 23
        }

        simple_model = SimpleModelForSerializer.objects.create(**values)
        # print simple_model.choice_field
        serializer = TheDjangoModelSerializer(simple_model)
        # values['id'] = simple_model.id
        # native_values['id'] = simple_model.id
        # # self.assertTrue(serializer.is_valid())
        # serializer.is_valid()
        # print serializer.errors_to_json(indent=4)
        # print serializer.to_json(indent=4)
        # self.assertDictEqual(serializer.to_dict(), values)
        # self.assertDictEqual(serializer.dump(), native_values)
