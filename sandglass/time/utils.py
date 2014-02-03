import functools
import re

from pyramid.interfaces import ISettings
from zope.component import getUtility

CAMELCASE_RE = re.compile('(.)([A-Z]{1})')


def camelcase_to_underscore(name):
    """
    Convert camel case names to underscore.

    Return a String.

    """
    return CAMELCASE_RE.sub(r'\1_\2', name).lower()


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
