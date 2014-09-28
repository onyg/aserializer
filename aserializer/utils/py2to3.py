# -*- coding: utf-8 -*-

import sys
import types

PYTHON2 = sys.version_info[0] == 2
PYTHON3 = sys.version_info[0] == 3


if PYTHON3:
    string = str,
    integer = int,
    _class = type,
    text = str
    binary = bytes
else:
    string = basestring,
    integer = (int, long)
    _class = (type, types.ClassType)
    text = unicode
    binary = str

if PYTHON3:
    def _unicode(o, encode=None):
        return str(o)
else:
    def _unicode(o, encode=None):
        if encode:
            return unicode(o, encode)
        return unicode(o)


if PYTHON3:
    def iterkeys(d, **kw):
        return iter(d.keys(**kw))

    def itervalues(d, **kw):
        return iter(d.values(**kw))

    def iteritems(d, **kw):
        return iter(d.items(**kw))

    def iterlists(d, **kw):
        return iter(d.lists(**kw))
else:
    def iterkeys(d, **kw):
        return iter(d.iterkeys(**kw))

    def itervalues(d, **kw):
        return iter(d.itervalues(**kw))

    def iteritems(d, **kw):
        return iter(d.iteritems(**kw))

    def iterlists(d, **kw):
        return iter(d.iterlists(**kw))


def with_metaclass(meta, *bases):
    class metaclass(meta):
        def __new__(cls, name, this_bases, d):
            return meta(name, bases, d)
    return type.__new__(metaclass, 'temporary_class', (), {})