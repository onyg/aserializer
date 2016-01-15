# -*- coding: utf-8 -*-

import unittest

from tests.django_tests import django, SKIPTEST_TEXT, TestCase
from tests.django_tests.django_app.models import RelOneDjangoModel, RelTwoDjangoModel, RelThreeDjangoModel
from tests.django_tests.django_base import (
    SimpleDjangoModel, RelatedDjangoModel, SimpleDjangoSerializer, RelatedDjangoSerializer,
    SecondSimpleDjangoSerializer, RelOneDjangoSerializer, NonModelFieldsDjangoSerializer,
    RelatedNonModelFieldsDjangoSerializer, Related2NonModelFieldsDjangoSerializer)


@unittest.skipIf(django is None, SKIPTEST_TEXT)
class DjangoSerializerTests(TestCase):

    def tearDown(self):
        SimpleDjangoModel.objects.all().delete()
        RelatedDjangoModel.objects.all().delete()

    def test_serialize(self):
        sdm = SimpleDjangoModel.objects.create(name='The Name', code='AAAA', number=1)

        serializer = SimpleDjangoSerializer(sdm)
        self.assertTrue(serializer.is_valid())
        self.assertDictEqual(serializer.dump(), dict(name='The Name', code='AAAA', number=1))

    def test_relation(self):
        sdm = SimpleDjangoModel.objects.create(name='The Name', code='AAAA', number=1)
        rdm = RelatedDjangoModel.objects.create(name='Relation', relation=sdm)

        serializer = RelatedDjangoSerializer(rdm)
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
        # TODO: this could eventually be more lazy
        with self.assertNumQueries(1):
            serializer = SecondSimpleDjangoSerializer(sdm)
        with self.assertNumQueries(0):
            self.assertTrue(serializer.is_valid())
        with self.assertNumQueries(0):
            model_dump = serializer.dump()
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
        self.assertDictEqual(model_dump, test_value)


@unittest.skipIf(django is None, SKIPTEST_TEXT)
class DjangoComplexSerializerTests(TestCase):

    def test_complex_related(self):
        rel_one = RelOneDjangoModel.objects.create(name='Rel One')
        rel_two = RelTwoDjangoModel.objects.create(name='Rel Two', rel_one=rel_one)
        rel_three1 = RelThreeDjangoModel.objects.create(name='Rel Three 1', rel_two=rel_two)
        rel_three2 = RelThreeDjangoModel.objects.create(name='Rel Three 2', rel_two=rel_two)

        with self.assertNumQueries(1):
            serializer = RelOneDjangoSerializer(rel_one)
        with self.assertNumQueries(0):
            self.assertTrue(serializer.is_valid())
        with self.assertNumQueries(0):
            model_dump = serializer.dump()
        test_value = {'name': 'Rel One', 'rel_twos': [{'name': 'Rel Two'}]}
        self.assertDictEqual(model_dump, test_value)


@unittest.skipIf(django is None, SKIPTEST_TEXT)
class DjangoNonModelFieldsSerializerTests(TestCase):

    def test_django_non_model_fields(self):
        sdm = SimpleDjangoModel.objects.create(name='The Name', code='AAAA', number=1)
        serializer = NonModelFieldsDjangoSerializer(sdm)
        self.assertTrue(serializer.is_valid())
        self.assertDictEqual(serializer.dump(), dict(name='The Name', _type='non-model', _type2='non-model2'))

    def test_django_related_non_model_fields(self):
        sdm = SimpleDjangoModel.objects.create(name='The Name', code='AAAA', number=1)
        RelatedDjangoModel.objects.create(name='Relation 1', relation=sdm)
        RelatedDjangoModel.objects.create(name='Relation 2', relation=sdm)

        # TODO: this could be eventually 1, maximum 2 queries
        with self.assertNumQueries(3):
            serializer = RelatedNonModelFieldsDjangoSerializer(sdm)
        with self.assertNumQueries(0):
            self.assertTrue(serializer.is_valid())
        with self.assertNumQueries(0):
            model_dump = serializer.dump()
        test_value = {
            '_type': 'non-model-related',
            'name': 'The Name',
            'relations': [
                {'_type': 'non-model',
                 # '_type2': 'non-model2',
                 'name': 'Relation 1'},
                {'_type': 'non-model',
                 # '_type2': 'non-model2',
                 'name': 'Relation 2'}
            ]
        }
        self.assertDictEqual(model_dump, test_value)

    def test_django_related2_non_model_fields(self):
        sdm = SimpleDjangoModel.objects.create(name='The Name', code='AAAA', number=1)
        RelatedDjangoModel.objects.create(name='Relation 1', relation=sdm)
        RelatedDjangoModel.objects.create(name='Relation 2', relation=sdm)

        with self.assertNumQueries(1):
            serializer = Related2NonModelFieldsDjangoSerializer(sdm)
        with self.assertNumQueries(0):
            self.assertTrue(serializer.is_valid())
        with self.assertNumQueries(0):
            model_dump = serializer.dump()
        test_value = {
            '_type': 'non-model-related',
            'name': 'The Name',
            'relations': [
                {'_type': 'non-model',
                 # '_type2': 'non-model2'
                 },
                {'_type': 'non-model',
                 # '_type2': 'non-model2'
                 }
            ]
        }
        self.assertDictEqual(model_dump, test_value)
