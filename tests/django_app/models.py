# -*- coding: utf-8 -*-

from django.db import models


class SimpleDjangoModel(models.Model):
    name = models.CharField(max_length=24, blank=False)
    code = models.CharField(max_length=4)
    number = models.IntegerField(blank=False)


class RelatedDjangoModel(models.Model):
    name = models.CharField(max_length=24, blank=False)
    relation = models.ForeignKey(SimpleDjangoModel, related_name='relations')
