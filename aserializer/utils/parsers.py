# -*- coding: utf-8 -*-

import json

from aserializer.utils import py2to3



class Parser(object):

    def __init__(self, fields=None):
        self.obj = None
        self._attribute_names = None
        self.field_list = fields or []

    def initial(self, source):
        if isinstance(source, py2to3.string):
            if not isinstance(source, py2to3.text):
                source = py2to3._unicode(source, 'utf-8')
            try:
                self.obj = json.loads(source)
            except ValueError:
                self.obj = object()
        else:
            self.obj = source
        self._attribute_names = None

    def get_object_members(self, obj):
        result = []
        for member in dir(obj):
            if not member.startswith('__'):
                result.append(member)
        return result

    @property
    def attribute_names(self):
        """
        This method returns a list of all variables/attributes of the object.
        """
        if self._attribute_names is not None:
            return self._attribute_names
        if self.obj is None:
            self._attribute_names = []
        elif isinstance(self.obj, dict):
            self._attribute_names = list(self.obj.keys())
        else:
            self._attribute_names = self.get_object_members(self.obj)
        return self._attribute_names

    def has_attribute(self, name):
        """
        This method checks if the source object got an variable for a field.
        """
        if isinstance(self.obj, dict):
            return name in self.obj
        else:
            return hasattr(self.obj, name)

    def get_value(self, name):
        """
        This method returns the value for one field from the source object.
        """
        if isinstance(self.obj, dict):
            value = self.obj.get(name, None)
        else:
            value = getattr(self.obj, name, None)
        return value
