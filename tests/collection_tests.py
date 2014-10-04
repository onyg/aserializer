# -*- coding: utf-8 -*-

import unittest

from aserializer.collection.base import CollectionSerializer, CollectionMetaOptions
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

    def test_pre_sort(self):
        collection = TestCollectionSerializer([])
        objects = [
            dict(name='3', number=5),
            dict(name='1', number=6),
            dict(name='2', number=7)
        ]
        olist = collection._pre(objects, sort=['name'])
        self.assertEqual(len(olist), 3)
        self.assertEqual(olist[0]['name'], '1')
        self.assertEqual(olist[1]['name'], '2')
        self.assertEqual(olist[2]['name'], '3')

        olist = collection._pre(objects, sort=['-number'])
        self.assertEqual(len(olist), 3)
        self.assertEqual(olist[0]['name'], '2')
        self.assertEqual(olist[1]['name'], '1')
        self.assertEqual(olist[2]['name'], '3')

    def test_metadata(self):
        collection = TestCollectionSerializer([])
        objects = [
            dict(name='The Name', number=9),
            dict(name='The Name 2', number=10),
            dict(name='The Name 3', number=8)
        ]
        metadata = collection.metadata(objects)
        self.assertIn('totalCount', metadata)
        self.assertIn('limit', metadata)
        self.assertIn('offset', metadata)
        self.assertEqual(metadata['totalCount'], 3)
        self.assertEqual(metadata['limit'], 10)
        self.assertEqual(metadata['offset'], 0)

    def test_metadata_changed(self):
        collection = TestCollectionSerializer([], limit=2, offset=1)
        objects = [
            dict(name='The Name', number=9),
            dict(name='The Name 2', number=10),
            dict(name='The Name 3', number=8)
        ]
        metadata = collection.metadata(objects)
        self.assertIn('totalCount', metadata)
        self.assertIn('limit', metadata)
        self.assertIn('offset', metadata)
        self.assertEqual(metadata['totalCount'], 3)
        self.assertEqual(metadata['limit'], 2)
        self.assertEqual(metadata['offset'], 1)


class MetaOptionTests(unittest.TestCase):

    def check_hasattr(self, meta):
        self.assertTrue(hasattr(meta,'serializer'))
        self.assertTrue(hasattr(meta,'with_metadata'))
        self.assertTrue(hasattr(meta,'metadata_key'))
        self.assertTrue(hasattr(meta,'items_key'))
        self.assertTrue(hasattr(meta,'offset_key'))
        self.assertTrue(hasattr(meta,'limit_key'))
        self.assertTrue(hasattr(meta,'total_count_key'))
        self.assertTrue(hasattr(meta,'fields'))
        self.assertTrue(hasattr(meta,'exclude'))
        self.assertTrue(hasattr(meta,'sort'))
        self.assertTrue(hasattr(meta,'validation'))

    def check_defaults(self, meta):
        self.assertIsNone(meta.serializer)
        self.assertTrue(meta.with_metadata)
        self.assertEqual(meta.metadata_key, '_metadata')
        self.assertEqual(meta.items_key, 'items')
        self.assertEqual(meta.offset_key, 'offset')
        self.assertEqual(meta.limit_key, 'limit')
        self.assertEqual(meta.total_count_key, 'totalCount')
        self.assertEqual(meta.fields, [])
        self.assertEqual(meta.exclude, [])
        self.assertEqual(meta.sort, [])
        self.assertTrue(meta.validation)

    def test_meta_options_class_defaults(self):
        meta = CollectionMetaOptions(None)
        self.check_hasattr(meta)
        self.check_defaults(meta)

    def test_no_META(self):
        class Collection(CollectionSerializer):
            ITEM_SERIALIZER_CLS = TestSerializer
        collection = Collection([])
        self.assertTrue(hasattr(collection, '_meta'))
        self.check_defaults(collection._meta)

    def test_META(self):
        class Collection(CollectionSerializer):
            class META:
                serializer = TestSerializer
                fields = ['name']
                items_key = 'data'
                metadata_key = 'info'
                sort = ['foo', '-bar']
                validation = False
        collection = Collection([])
        self.assertTrue(hasattr(collection, '_meta'))
        self.check_hasattr(collection._meta)
        self.assertEqual(collection._meta.serializer, TestSerializer)
        self.assertEqual(collection._meta.fields, ['name'])
        self.assertEqual(collection._meta.sort, ['foo', '-bar'])
        self.assertEqual(collection._meta.items_key, 'data')
        self.assertEqual(collection._meta.metadata_key, 'info')
        self.assertFalse(collection._meta.validation)
