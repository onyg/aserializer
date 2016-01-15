# -*- coding: utf-8 -*-

import json
import inspect
from aserializer.utils import py2to3


class Parser(object):

    def __init__(self, fields=None):
        self.obj = None
        self._attribute_names = None
        self._all_attributes_names = None
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

    def _attribute_name_predicate(self, name, with_filter=False):
        if name.startswith('__'):
            return False
        if with_filter:
            return name in self.field_list
        else:
            if isinstance(self.obj, (tuple, list, set, dict,)):
                return True
            try:
                value = getattr(self.obj, name)
            except AttributeError:
                return False
            return not inspect.ismethod(value)

    def get_attribute_names(self, with_filter=False):
        """
        This method returns a list of all variables/attributes of the object.
        """
        if self.obj is None:
            return []
        if isinstance(self.obj, dict):
            return [name for name in self.obj.keys() if self._attribute_name_predicate(name, with_filter)]
        return [name for name in dir(self.obj) if self._attribute_name_predicate(name, with_filter)]

    @property
    def attributes_for_serializer(self):
        """
        This method returns a list of variables/attributes of the object related for the serializer fields..
        """
        if self._attribute_names is not None:
            return self._attribute_names
        self._attribute_names = self.get_attribute_names(with_filter=True)
        return self._attribute_names

    @property
    def all_attributes(self):
        """
        This method returns a list of all variables/attributes of the object.
        """
        if self._all_attributes_names is not None:
            return self._all_attributes_names
        self._all_attributes_names = self.get_attribute_names(with_filter=False)
        return self._all_attributes_names

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
