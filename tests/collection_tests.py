# -*- coding: utf-8 -*-

import unittest

from aserializer.collection.base import CollectionSerializer
from aserializer import Serializer
from aserializer.fields import StringField, IntegerField


class TestSerializer(Serializer):
    name = StringField(required=True)
    number = IntegerField(required=True, max_value=10, min_value=5)


class TestCollectionSerializer(CollectionSerializer):

    class META:
        serializer = TestSerializer


class TestObject(object):
    def __init__(self, name, number):
        self.name = name
        self.number = number


class CollectionDumpTestCase(unittest.TestCase):

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

    def test_with_objects(self):
        objects = [
            TestObject(name='The Name', number=9),
            TestObject(name='The Name 2', number=10)
        ]
        collection = TestCollectionSerializer(objects=objects)
        self.assertEqual(len(collection), 2)
        self.assertIn('_metadata', collection.dump())
        self.assertIn('items', collection.dump())
        self.assertEqual(len(collection.dump()['items']), 2)
        self.assertEqual(collection.dump()['_metadata']['totalCount'], 2)
        self.assertEqual(collection.dump()['_metadata']['offset'], 0)
        self.assertListEqual(collection.dump()['items'], [{'name':o.name, 'number':o.number} for o in objects])


class CollectionTestCase(unittest.TestCase):

    def test_item(self):
        collection = TestCollectionSerializer([])
        dump = collection.item(TestObject(name='The Name', number=9))
        self.assertIn('name', dump)
        self.assertIn('number', dump)
        self.assertDictEqual(dump, {'name':'The Name', 'number':9})

    def test_item_with_invaild_serializer(self):
        collection = TestCollectionSerializer([])
        dump = collection.item(dict(wrongkey='The Name', number=9))
        self.assertDictEqual(dump, {})
        dump = collection.item(dict(name='The Name', number=15))
        self.assertDictEqual(dump, {})

    def test_items(self):
        collection = TestCollectionSerializer([])
        objects = [
            TestObject(name='The Name', number=9),
            TestObject(name='The Name 2', number=10)
        ]
        dump = collection._items(objects)
        self.assertEqual(len(dump), 2)
        self.assertListEqual(dump, [{'name':o.name, 'number':o.number} for o in objects])

    def test_pre(self):
        collection = TestCollectionSerializer([])
        objects = [
            dict(name='The Name', number=9),
            dict(name='The Name 2', number=10)
        ]
        olist = collection._pre(objects)
        self.assertEqual(len(olist), 2)
        self.assertListEqual(olist, objects)

        olist = collection._pre(objects, limit=1)
        self.assertEqual(len(olist), 1)
        self.assertListEqual(olist, [objects[0]])

        olist = collection._pre(objects, limit=1, offset=1)
        self.assertEqual(len(olist), 1)
        self.assertListEqual(olist, [objects[1]])

        olist = collection._pre(objects, limit=1, offset=-1)
        self.assertEqual(len(olist), 0)
        self.assertListEqual(olist, [])

