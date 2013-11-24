# -*- coding: utf-8 -*-


_serializer_registry = {}


class SerializerNotRegistered(Exception):
    message = 'Not in register.'


def register_serializer(name, cls):
    if name in _serializer_registry:
        return
    _serializer_registry[name] = cls


def get_serializer(name):
    if name in _serializer_registry:
        return _serializer_registry[name]
    raise SerializerNotRegistered()
