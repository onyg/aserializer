# -*- coding: utf-8 -*-

import inspect
import json

from aserializer.utils import py2to3


class Parser(object):

    def __init__(self):
        self.obj = None
        self._attribute_names = None

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
            def get_members(obj):
                result = []
                for key in dir(obj):
                    if key.startswith('__'):
                        continue
                    try:
                        value = getattr(obj, key)
                    except AttributeError:
                        continue
                    if not inspect.ismethod(value):
                        result.append(key)
                return result
            self._attribute_names = get_members(self.obj)
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
