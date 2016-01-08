# -*- coding: utf-8 -*-
import unittest

from tests.django_tests import django, SKIPTEST_TEXT, TestCase
from tests.django_tests.django_base import (SimpleDjangoModel, RelatedDjangoModel, SimpleDjangoModelCollection,)


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