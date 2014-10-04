# -*- coding: utf-8 -*-
from aserializer.utils import py2to3

_serializer_registry = {}


class SerializerNotRegistered(Exception):
    message = 'Not in register.'


def register_serializer(name, cls):
    if name in _serializer_registry:
        return
    _serializer_registry[name] = cls


def get_serializer(serializer):
    if isinstance(serializer, py2to3.string):
        name = serializer
    elif isinstance(serializer, py2to3._class):
        name = serializer.__name__
    elif serializer is None:
        raise AttributeError('Can not get a serializer class from None.')
    else:
        raise AttributeError('Not a class.')
    if name in _serializer_registry:
        return _serializer_registry[name]
    raise SerializerNotRegistered()
