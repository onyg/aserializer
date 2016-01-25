# -*- coding: utf-8 -*-

from django.db import models
from django import VERSION as DJANGO_VERSION


class SimpleDjangoModel(models.Model):
    name = models.CharField(max_length=24, blank=False)
    code = models.CharField(max_length=4)
    number = models.IntegerField(blank=False)


class RelatedDjangoModel(models.Model):
    name = models.CharField(max_length=24, blank=False)
    relation = models.ForeignKey(SimpleDjangoModel, related_name='relations')


class SimpleModelForSerializer(models.Model):
    _CHOICES = (
        ('Zero', 'Linux'),
        ('One', 'Windows'),
        ('Two', 'OSX'),
        ('Three', 'DOS'),
    )

    char_field = models.CharField(max_length=40)
    integer_field = models.IntegerField(blank=True, null=True)
    integer_field2 = models.IntegerField(max_length=3)
    positiveinteger_field = models.PositiveIntegerField()
    float_field = models.FloatField()
    date_field = models.DateField()
    datetime_field = models.DateTimeField()
    time_field = models.TimeField()
    boolean_field = models.BooleanField(default=True)
    decimal_field = models.DecimalField(decimal_places=3, max_digits=5)
    text_field = models.TextField()
    commaseparatedinteger_field = models.CommaSeparatedIntegerField(max_length=60)
    choice_field = models.CharField(max_length=4, choices=_CHOICES)
    url_field = models.URLField()


class RelOneDjangoModel(models.Model):
    name = models.CharField(max_length=24, blank=False)


class RelTwoDjangoModel(models.Model):
    name = models.CharField(max_length=24, blank=False)
    rel_one = models.ForeignKey(RelOneDjangoModel, related_name='rel_twos')


class RelThreeDjangoModel(models.Model):
    name = models.CharField(max_length=24, blank=False)
    rel_two = models.ForeignKey(RelTwoDjangoModel, related_name='rel_threes')
    rel_one = models.ForeignKey(RelOneDjangoModel, null=True, related_name='rel_threes')


class M2MOneDjangoModel(models.Model):
    name = models.CharField(max_length=24)
    simple_model = models.ForeignKey(SimpleDjangoModel, null=True, related_name='ones')


class M2MTwoDjangoModel(models.Model):
    name = models.CharField(max_length=24)
    ones = models.ManyToManyField(M2MOneDjangoModel, related_name='twos')


class One2One1DjangoModel(models.Model):
    name = models.CharField(max_length=24)


class One2One2DjangoModel(models.Model):
    name = models.CharField(max_length=24)
    one1 = models.OneToOneField(One2One1DjangoModel, related_name='one2')


if DJANGO_VERSION >= (1, 8, 0):

    class UUIDFieldModel(models.Model):
        name = models.CharField(max_length=24)
        uuid_field = models.UUIDField()
else:
    class UUIDFieldModel(models.Model):
        name = models.CharField(max_length=24)


class FieldArgsDjangoModel(models.Model):
    name = models.CharField(max_length=24, null=True, blank=True)


class FieldArgsRelatedDjangoModel(models.Model):
    name = models.CharField(max_length=24, null=True, blank=True)
    relation = models.ForeignKey(FieldArgsDjangoModel, related_name='relations')
