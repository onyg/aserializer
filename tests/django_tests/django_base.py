# -*- coding: utf-8 -*-


from aserializer import Serializer
from aserializer import fields
from aserializer.django.fields import RelatedManagerListSerializerField
from aserializer.django.collection import DjangoCollectionSerializer
from aserializer.django.serializers import DjangoModelSerializer, DjangoModelSerializerBase

from tests.django_tests import django

if django is not None:
    from tests.django_tests.django_app.models import (
        SimpleDjangoModel,
        RelatedDjangoModel,
        SimpleModelForSerializer,
    )


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


class TheDjangoModelSerializer(DjangoModelSerializer):

    class Meta:
        model = SimpleModelForSerializer if django else None


class SimpleDjangoModelCollection(DjangoCollectionSerializer):
    class Meta:
        serializer = SimpleDjangoModelSerializer