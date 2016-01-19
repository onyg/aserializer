# -*- coding: utf-8 -*-

import unittest
from datetime import datetime
from decimal import Decimal

from tests.django_tests import django, SKIPTEST_TEXT, TestCase
from tests.django_tests.django_app.models import One2One1DjangoModel, One2One2DjangoModel
from tests.django_tests.django_base import (
    TheDjangoModelSerializer, SimpleModelForSerializer, RelOneDjangoModel, RelTwoDjangoModel,
    RelThreeDjangoModel, RelDjangoModelSerializer, RelReverseDjangoModelSerializer,
    M2MTwoDjangoModel, M2MOneDjangoModel, M2MOneDjangoModelSerializer, M2MTwoDjangoModelSerializer,
    One2One2DjangoModelSerializer, One2One1DjangoModelSerializer, OnlyNameFieldDjangoModelSerializer,
    OnlyNameAndRelatedNameFieldsDjangoModelSerializer, ExcludeFieldsDjangoModelSerializer,
    ExcludeReverseRelatedFieldDjangoModelSerializer,)


@unittest.skipIf(django is None, SKIPTEST_TEXT)
class RelDjangoSerializerTests(TestCase):

    def tearDown(self):
        RelOneDjangoModel.objects.all().delete()
        RelTwoDjangoModel.objects.all().delete()
        RelThreeDjangoModel.objects.all().delete()

    def test_three_level_reverse_relations(self):
        one = RelOneDjangoModel.objects.create(name='Level1')
        two = RelTwoDjangoModel.objects.create(name='Level2', rel_one=one)
        three = RelThreeDjangoModel.objects.create(name='Level3', rel_two=two)

        with self.assertNumQueries(3):
            serializer = RelReverseDjangoModelSerializer(one)
        with self.assertNumQueries(0):
            self.assertTrue(serializer.is_valid())
        with self.assertNumQueries(0):
            model_dump = serializer.dump()
        test_value = {
            'rel_twos': [
                {'rel_threes':
                    [
                        {
                            'id': 1,
                            'name': 'Level3'
                         }
                     ],
                 'id': 1,
                 'name': 'Level2'
                 }
            ],
            'rel_threes': [],
            'id': 1,
            'name': 'Level1'}
        self.assertDictEqual(model_dump, test_value)

    def test_three_level_relations(self):
        one = RelOneDjangoModel.objects.create(name='Level1')
        two = RelTwoDjangoModel.objects.create(name='Level2', rel_one=one)
        three = RelThreeDjangoModel.objects.create(name='Level3', rel_two=two)

        with self.assertNumQueries(0):
            serializer = RelDjangoModelSerializer(three)
        with self.assertNumQueries(0):
            self.assertTrue(serializer.is_valid())
        with self.assertNumQueries(0):
            obj_dump = serializer.dump()

        with self.assertNumQueries(3):
            serializer = RelDjangoModelSerializer(RelThreeDjangoModel.objects.first())
        with self.assertNumQueries(0):
            self.assertTrue(serializer.is_valid())
        with self.assertNumQueries(0):
            qs_obj_dump = serializer.dump()

        test_value = {
            'rel_two': {
                'rel_one': {
                    'id': 1,
                    'name': 'Level1'},
                'id': 1,
                'name': 'Level2'},
            'rel_one': None,
            'id': 1,
            'name': 'Level3'
        }
        self.assertDictEqual(obj_dump, test_value)
        self.assertDictEqual(qs_obj_dump, test_value)

    def test_three_level_relations_with_exclude(self):
        one = RelOneDjangoModel.objects.create(name='Level1')
        two = RelTwoDjangoModel.objects.create(name='Level2', rel_one=one)
        RelThreeDjangoModel.objects.create(name='Level3', rel_two=two)
        with self.assertNumQueries(2):
            serializer = RelDjangoModelSerializer(RelThreeDjangoModel.objects.first(), exclude=['rel_two.rel_one'])
        with self.assertNumQueries(0):
            self.assertTrue(serializer.is_valid())
        with self.assertNumQueries(0):
            model_dump = serializer.dump()
        test_value = {
            'rel_two': {
                'id': 1,
                'name': 'Level2'},
            'rel_one': None,
            'id': 1,
            'name': 'Level3'
        }
        self.assertDictEqual(model_dump, test_value)

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


@unittest.skipIf(django is None, SKIPTEST_TEXT)
class M2MSerializerTests(TestCase):
    maxDiff = None

    def test_explicit_m2m(self):
        one = M2MOneDjangoModel.objects.create(name='One-One')
        two = one.twos.create(name='Two')
        two.ones.add(M2MOneDjangoModel.objects.create(name='One-Two'))

        serializer = M2MTwoDjangoModelSerializer(two)
        self.assertTrue(serializer.is_valid())
        test_value = {
            'ones': [
                {
                    'id': 1,
                    'name': 'One-One'
                },
                {
                    'id': 2,
                    'name': 'One-Two'
                }
            ],
            'id': 1,
            'name': 'Two'
        }
        self.assertDictEqual(serializer.dump(), test_value)

    def test_related_m2m(self):
        one = M2MOneDjangoModel.objects.create(name='One-One')
        two = one.twos.create(name='Two')
        two.ones.add(M2MOneDjangoModel.objects.create(name='One-Two'))

        serializer = M2MOneDjangoModelSerializer(one)
        self.assertTrue(serializer.is_valid())
        test_value = {
            'twos': [
                {
                    'id': 1,
                    'name': 'Two'
                }
            ],
            'id': 1,
            'name': 'One-One'
        }
        self.assertDictEqual(serializer.dump(), test_value)


@unittest.skipIf(django is None, SKIPTEST_TEXT)
class One2OneSerializerTests(TestCase):
    maxDiff = None

    def test_explicit_one2one(self):
        one1 = One2One1DjangoModel.objects.create(name='One2One-1')
        one2 = One2One2DjangoModel.objects.create(name='One2One-2', one1=one1)

        serializer = One2One2DjangoModelSerializer(one2)
        self.assertTrue(serializer.is_valid())
        test_value = {
            'one1': {
                'id': 1,
                'name': 'One2One-1'
            },
            'id': 1,
            'name': 'One2One-2'
        }
        self.assertDictEqual(serializer.dump(), test_value)

    def test_related_one2one(self):
        one1 = One2One1DjangoModel.objects.create(name='One2One-1')
        one2 = One2One2DjangoModel.objects.create(name='One2One-2', one1=one1)

        serializer = One2One1DjangoModelSerializer(one1)
        self.assertTrue(serializer.is_valid())
        test_value = {
            'one2': {
                'id': 1,
                'name': 'One2One-2'
            },
            'id': 1,
            'name': 'One2One-1'
        }
        self.assertDictEqual(serializer.dump(), test_value)


@unittest.skipIf(django is None, SKIPTEST_TEXT)
class OnlyAndExcludeSerializerTests(TestCase):
    maxDiff = None

    def test_only_name_field(self):
        one = RelOneDjangoModel.objects.create(name='Level1')
        two = RelTwoDjangoModel.objects.create(name='Level2', rel_one=one)
        RelThreeDjangoModel.objects.create(name='Level3', rel_two=two)

        with self.assertNumQueries(1):
            serializer = OnlyNameFieldDjangoModelSerializer(RelThreeDjangoModel.objects.first())
        with self.assertNumQueries(0):
            self.assertTrue(serializer.is_valid())
        with self.assertNumQueries(0):
            model_dump = serializer.dump()
        test_value = {
            'id': 1,
            'name': 'Level3'
        }
        self.assertDictEqual(model_dump, test_value)

    def test_only_name_field_with_no_extra_queries(self):
        one = RelOneDjangoModel.objects.create(name='Level1')
        two = RelTwoDjangoModel.objects.create(name='Level2', rel_one=one)
        three = RelThreeDjangoModel.objects.create(name='Level3', rel_two=two)

        with self.assertNumQueries(0):
            serializer = OnlyNameFieldDjangoModelSerializer(three)
        with self.assertNumQueries(0):
            self.assertTrue(serializer.is_valid())
        with self.assertNumQueries(0):
            model_dump = serializer.dump()
        test_value = {
            'id': 1,
            'name': 'Level3'
        }
        self.assertDictEqual(model_dump, test_value)


    def test_only_name_and_relation_name_field(self):
        one = RelOneDjangoModel.objects.create(name='Level1')
        two = RelTwoDjangoModel.objects.create(name='Level2', rel_one=one)
        three = RelThreeDjangoModel.objects.create(name='Level3', rel_one=one, rel_two=two)

        with self.assertNumQueries(0):
            serializer = OnlyNameAndRelatedNameFieldsDjangoModelSerializer(three)
        with self.assertNumQueries(0):
            self.assertTrue(serializer.is_valid())
        with self.assertNumQueries(0):
            model_dump = serializer.dump()
        test_value = {
            'id': 1,
            'name': 'Level3',
            'rel_one':{
                'id': 1,
                'name': 'Level1'
            }
        }
        self.assertDictEqual(model_dump, test_value)

    def test_only_name_and_relation_name_field_with_no_extra_queries(self):
        one = RelOneDjangoModel.objects.create(name='Level1')
        two = RelTwoDjangoModel.objects.create(name='Level2', rel_one=one)
        RelThreeDjangoModel.objects.create(name='Level3', rel_one=one, rel_two=two)

        with self.assertNumQueries(2):
            serializer = OnlyNameAndRelatedNameFieldsDjangoModelSerializer(RelThreeDjangoModel.objects.first())
        with self.assertNumQueries(0):
            self.assertTrue(serializer.is_valid())
        with self.assertNumQueries(0):
            model_dump = serializer.dump()
        test_value = {
            'id': 1,
            'name': 'Level3',
            'rel_one':{
                'id': 1,
                'name': 'Level1'
            }
        }
        self.assertDictEqual(model_dump, test_value)

    def test_exclude_fields(self):
        one = RelOneDjangoModel.objects.create(name='Level1')
        two = RelTwoDjangoModel.objects.create(name='Level2', rel_one=one)
        RelThreeDjangoModel.objects.create(name='Level3', rel_one=one, rel_two=two)

        with self.assertNumQueries(1):
            serializer = ExcludeFieldsDjangoModelSerializer(RelThreeDjangoModel.objects.first())
        with self.assertNumQueries(0):
            self.assertTrue(serializer.is_valid())
        with self.assertNumQueries(0):
            model_dump = serializer.dump()
        test_value = {
            'id': 1,
            'name': 'Level3',
        }
        self.assertDictEqual(model_dump, test_value)

    def test_exclude_fields_with_no_extra_queries(self):
        one = RelOneDjangoModel.objects.create(name='Level1')
        two = RelTwoDjangoModel.objects.create(name='Level2', rel_one=one)
        three = RelThreeDjangoModel.objects.create(name='Level3', rel_one=one, rel_two=two)

        with self.assertNumQueries(0):
            serializer = ExcludeFieldsDjangoModelSerializer(three)
        with self.assertNumQueries(0):
            self.assertTrue(serializer.is_valid())
        with self.assertNumQueries(0):
            model_dump = serializer.dump()
        test_value = {
            'id': 1,
            'name': 'Level3',
        }
        self.assertDictEqual(model_dump, test_value)

    def test_reverse_related_exclude(self):
        one = M2MOneDjangoModel.objects.create(name='One-One')
        two0 = one.twos.create(name='Two0')
        two0.ones.add(M2MOneDjangoModel.objects.create(name='Zero-Two'))
        two1 = one.twos.create(name='Two1')
        two1.ones.add(M2MOneDjangoModel.objects.create(name='One-Two'))

        with self.assertNumQueries(1):
            serializer = ExcludeReverseRelatedFieldDjangoModelSerializer(one)
        with self.assertNumQueries(0):
            self.assertTrue(serializer.is_valid())
        with self.assertNumQueries(0):
            model_dump = serializer.dump()
        test_value = {
            'twos': [
                {'id': 1},
                {'id': 2}
            ],
            'id': 1
        }
        self.assertDictEqual(model_dump, test_value)

