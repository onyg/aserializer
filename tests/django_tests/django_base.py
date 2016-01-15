# -*- coding: utf-8 -*-
from aserializer import Serializer
from aserializer import fields
from aserializer.django.fields import RelatedManagerListSerializerField
from aserializer.django.collection import DjangoCollectionSerializer
from aserializer.django.serializers import DjangoModelSerializer

from tests.django_tests import django

if django is not None:
    from tests.django_tests.django_app.models import (
        SimpleDjangoModel,
        RelatedDjangoModel,
        SimpleModelForSerializer,
        RelOneDjangoModel,
        RelTwoDjangoModel,
        RelThreeDjangoModel,
        M2MOneDjangoModel,
        M2MTwoDjangoModel,
        One2One1DjangoModel, One2One2DjangoModel)

# First some manually defined serializers for django models


class SimpleDjangoSerializer(Serializer):
    name = fields.StringField(required=True, max_length=24)
    code = fields.StringField(max_length=4)
    number = fields.IntegerField(required=True)


class RelatedDjangoSerializer(Serializer):
    name = fields.StringField(required=True, max_length=24)
    relation = fields.SerializerField(SimpleDjangoSerializer)


class SecondSimpleDjangoSerializer(Serializer):
    name = fields.StringField(required=True, max_length=24)
    code = fields.StringField(max_length=4)
    number = fields.IntegerField(required=True)
    relations = RelatedManagerListSerializerField(RelatedDjangoSerializer, exclude=['relation'])


class RelThreeDjangoSerializer(Serializer):
    name = fields.StringField(required=True, max_length=24)
    rel_two = RelatedManagerListSerializerField('RelTwoDjangoSerializer', exclude=['rel_one'])
    rel_one = RelatedManagerListSerializerField('RelOneDjangoSerializer', required=False, exclude=['rel_twos'])


class RelTwoDjangoSerializer(Serializer):
    name = fields.StringField(required=True, max_length=24)
    rel_one = RelatedManagerListSerializerField('RelOneDjangoSerializer', exclude=['rel_twos'])


class RelOneDjangoSerializer(Serializer):
    name = fields.StringField(required=True, max_length=24)
    rel_twos = RelatedManagerListSerializerField('RelTwoDjangoSerializer', exclude=['rel_one'])


class NonModelFieldsDjangoSerializer(Serializer):
    name = fields.StringField(required=True, max_length=24)
    _type = fields.TypeField(name='non-model', validate=True, required=True)
    _type2 = fields.TypeField(name='non-model2', validate=True, required=True)


class RelatedNonModelFieldsDjangoSerializer(Serializer):
    name = fields.StringField(required=True, max_length=24)
    _type = fields.TypeField(name='non-model-related', validate=True, required=True)
    relations = RelatedManagerListSerializerField(NonModelFieldsDjangoSerializer, fields=('name', '_type',))


class Related2NonModelFieldsDjangoSerializer(Serializer):
    name = fields.StringField(required=True, max_length=24)
    _type = fields.TypeField(name='non-model-related', validate=True, required=True)
    relations = RelatedManagerListSerializerField(NonModelFieldsDjangoSerializer, fields=('_type',))


# Here some serializers using the Django Model introspection


class TheDjangoModelSerializer(DjangoModelSerializer):

    class Meta:
        model = SimpleModelForSerializer if django else None


class SimpleDjangoModelCollectionSerializer(DjangoCollectionSerializer):
    class Meta:
        serializer = SimpleDjangoSerializer


class RelDjangoModelSerializer(DjangoModelSerializer):

    class Meta:
        model = RelThreeDjangoModel


class RelReverseDjangoModelSerializer(DjangoModelSerializer):

    class Meta:
        model = RelOneDjangoModel


class M2MOneDjangoModelSerializer(DjangoModelSerializer):

    class Meta:
        model = M2MOneDjangoModel


class M2MTwoDjangoModelSerializer(DjangoModelSerializer):

    class Meta:
        model = M2MTwoDjangoModel


class One2One1DjangoModelSerializer(DjangoModelSerializer):

    class Meta:
        model = One2One1DjangoModel


class One2One2DjangoModelSerializer(DjangoModelSerializer):

    class Meta:
        model = One2One2DjangoModel
