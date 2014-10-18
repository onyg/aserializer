# -*- coding: utf-8 -*-

import os
import unittest

from aserializer import Serializer
from aserializer import fields
from aserializer.django.fields import RelatedManagerListSerializerField
from aserializer.django.collection import DjangoCollectionSerializer
from aserializer.django.serializers import ModelSerializer

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
    from tests.django_app.models import SimpleDjangoModel, RelatedDjangoModel
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

class TheModelSerializer(ModelSerializer):
    name = fields.StringField()

    class Meta:
        model = RelatedDjangoModel

class ModelSerializerTests(unittest.TestCase):

    def test_one(self):
        serializer = TheModelSerializer(dict(name='The Name', foo='THE MAGIC FOO'))
        # serializer.is_valid()
        # print serializer.errors_to_json(indent=4)
        # print serializer.to_json(indent=4)
        # # serializer.foo = 'Changed name'
        # # serializer.name = 'Changed name'
        # # print serializer.to_json(indent=4)

