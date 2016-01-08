# -*- coding: utf-8 -*-

import unittest
from datetime import datetime
from decimal import Decimal

from tests.django_tests import django, SKIPTEST_TEXT, TestCase
from tests.django_tests.django_base import (
    SimpleDjangoModel, RelatedDjangoModel, SimpleDjangoModelSerializer, RelatedDjangoModelSerializer,
    SecondSimpleDjangoModelSerializer, TheDjangoModelSerializer, SimpleModelForSerializer,)


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


@unittest.skipIf(django is None, SKIPTEST_TEXT)
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
            "choice_field": "Linux",
            "char_field": "test",
            "boolean_field": False,
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
        serializer = TheDjangoModelSerializer(simple_model)
        values['id'] = simple_model.id
        native_values['id'] = simple_model.id
        self.assertTrue(serializer.is_valid())
        self.assertDictEqual(serializer.to_dict(), values)
        self.assertDictEqual(serializer.dump(), native_values)
