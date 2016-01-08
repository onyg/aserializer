# -*- coding: utf-8 -*-

from django.db import models


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
