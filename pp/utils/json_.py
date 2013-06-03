'''
JSON Adapters

Created on May 30, 2013

@author: Edward Easton
'''
import json
import datetime
import logging

from zope.interface.registry import Components
from zope.interface import Interface, providedBy

# Singleton type registry
_TYPE_REGISTRY = Components()
_marker = object()


def get_log():
    return logging.getLogger('pp.utils.json')


class IJSONAdapter(Interface):
    """
    Marker interface for objects that can convert an arbitrary object
    into a JSON-serializable primitive.
    """


def get_adapters():
    """ Return (type, adapter) pairs for our global registry
    """
    # XXX this is super-sketchy! Learn to use the API properly ;)
    res = []
    for i in _TYPE_REGISTRY.adapters._adapters:
        for type_ in i:
            res.append((type_.inherit, i[type_][IJSONAdapter]['']))
    return res


def add_adapter(type_or_iface, adapter):
    """ Add adapter for a custom type to the global registry.

    Examples
    --------

    >>> class Foo(object):
    >>>     x = 5
    >>>
    >>> def foo_adapter(obj):
    >>>    return obj.x
    >>>
    >>> add_adapter(Foo, foo_adapter)
    >>> json.dumps(Foo(), cls=CustomEncoder)
    5
    """
    global _TYPE_REGISTRY
    _TYPE_REGISTRY.registerAdapter(adapter, (type_or_iface,), IJSONAdapter)


# Built-in adapters
def datetime_adapter(obj):
    return obj.isoformat()

add_adapter(datetime.datetime, datetime_adapter)


class CustomEncoder(json.JSONEncoder):
    """ Minimal version of the Pyramid JSON rendered - allow custom types to
        be encoded using ZCA adapters and support __json__ attribute on
        objects.
    """
    def default(self, obj):
        global __TYPE_REGISTRY
        if hasattr(obj, '__json__'):
            return obj.__json__()
        obj_iface = providedBy(obj)
        adapter = _TYPE_REGISTRY.adapters.lookup((obj_iface,),
                                                 IJSONAdapter,
                                                 default=_marker)
        if adapter is not _marker:
            return adapter(obj)

        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)
