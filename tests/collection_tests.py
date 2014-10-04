# -*- coding: utf-8 -*-

import unittest

from aserializer.collection.base import CollectionSerializer
from aserializer import Serializer
from aserializer.fields import StringField, IntegerField


class TestSerializer(Serializer):
    name = StringField(required=True)
    number = IntegerField(required=True, max_value=10, min_value=5)


class TestCollectionSerializer(CollectionSerializer):
    ITEM_SERIALIZER_CLS = TestSerializer


class CollectionTestCase(unittest.TestCase):

    def test_with_dict(self):
        objects = [
            dict(name='The Name', number=9),
            dict(name='The Name 2', number=10)
        ]
        collection = TestCollectionSerializer(objects=objects)
        self.assertEqual(len(collection), 2)
        self.assertIn('_metadata', collection.dump())
        self.assertIn('items', collection.dump())
        self.assertEqual(len(collection.dump()['items']), 2)
        self.assertEqual(collection.dump()['_metadata']['totalCount'], 2)
        self.assertEqual(collection.dump()['_metadata']['offset'], 0)
        self.assertListEqual(collection.dump()['items'], objects)

    def test_with_dict(self):
        objects = [
            dict(name='The Name', number=9),
            dict(name='The Name 2', number=10)
        ]
        collection = TestCollectionSerializer(objects=objects)
        self.assertEqual(len(collection), 2)
        self.assertIn('_metadata', collection.dump())
        self.assertIn('items', collection.dump())
        self.assertEqual(len(collection.dump()['items']), 2)
        self.assertEqual(collection.dump()['_metadata']['totalCount'], 2)
        self.assertEqual(collection.dump()['_metadata']['offset'], 0)
        self.assertListEqual(collection.dump()['items'], objects)
