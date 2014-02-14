import functools
import re

import pyramid.url

from pyramid.interfaces import ISettings
from pyramid.testing import DummyRequest
from zope.component import getUtility

# Regexps for underscore/camelcase convertions
CAMELCASE_RE = re.compile("(.)([A-Z]{1})")
UNDERSCORE_RE = re.compile(r"(?:^|_)(.)")


def camelcase_to_underscore(name):
    """
    Convert camelcase names to underscore.

    Return a String.

    """
    return CAMELCASE_RE.sub(r'\1_\2', name).lower()


def underscore_to_camelcase(name):
    """
    Convert underscore names to camelcase.

    Return a String.

    """
    def replace_fn(match):
        """
        Upercase first char after "_".

        Return a char.

        """
        return match.group(1).upper()

    if not name:
        return name

    name = UNDERSCORE_RE.sub(replace_fn, name)
    return (name[0].lower() + name[1:])


def camelcase_dict(obj):
    """
    Create a new dictionary with camelcase keys using the given one.

    Return a Dictionary.

    """
    u2c = underscore_to_camelcase
    return {u2c(key): value for (key, value) in obj.iteritems()}


def underscore_dict(obj):
    """
    Create a new dictionary with underscore keys using the given one.

    Return a Dictionary.

    """
    c2u = camelcase_to_underscore
    return {c2u(key): value for (key, value) in obj.iteritems()}


class mixedmethod(object):
    """
    Decorator that allows a method to be both a class method
    and an instance method at the same time.

    """
    def __init__(self, method):
        self.method = method

    def __get__(self, obj=None, objtype=None):
        @functools.wraps(self.method)
        def _wrapper(*args, **kwargs):
            if obj is not None:
                return self.method(obj, *args, **kwargs)
            else:
                return self.method(objtype, *args, **kwargs)
        return _wrapper


def get_settings():
    """
    Get application settings.

    Return a Dictionary.

    """
    return getUtility(ISettings)


def route_path(route_name, request=None, **kwargs):
    """
    Get a route path for an existing route.

    A `DummyRequest` is used when no request is given.

    Return a String.

    """
    if not request:
        request = DummyRequest()

    return pyramid.url.route_path(route_name, request, **kwargs)
