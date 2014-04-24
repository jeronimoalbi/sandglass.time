# pylint: disable=W0622,C0103

import functools
import hashlib
import os
import re

from inspect import isclass

import pyramid.url

from colander import EMAIL_RE
from pyramid.testing import DummyRequest
from pyramid.threadlocal import get_current_registry

# Regexps for underscore/camelcase convertions
CAMELCASE_RE = re.compile("(.)([A-Z]{1})")
UNDERSCORE_RE = re.compile(r"(?:^|_)(.)")


def get_settings():
    """
    Get application settings.

    Application settings are customized in the ".ini" file.

    Returns a Dictionary.

    """
    return get_current_registry().settings


def is_valid_email(email):
    """
    Check if a string is a valid email.

    Returns a Boolean.

    """
    return re.match(EMAIL_RE, email) is not None


def camelcase_to_underscore(name):
    """
    Convert camelcase names to underscore.

    Returns a String.

    """
    return CAMELCASE_RE.sub(r'\1_\2', name).lower()


def underscore_to_camelcase(name):
    """
    Convert underscore names to camelcase.

    Returns a String.

    """
    def replace_fn(match):
        """
        Upercase first char after "_".

        Returns a char.

        """
        return match.group(1).upper()

    if not name:
        return name

    name = UNDERSCORE_RE.sub(replace_fn, name)
    return name[0].lower() + name[1:]


def camelcase_dict(obj):
    """
    Create a new dictionary with camelcase keys using the given one.

    Returns a Dictionary.

    """
    u2c = underscore_to_camelcase
    return {u2c(key): value for (key, value) in obj.iteritems()}


def underscore_dict(obj):
    """
    Create a new dictionary with underscore keys using the given one.

    Returns a Dictionary.

    """
    c2u = camelcase_to_underscore
    return {c2u(key): value for (key, value) in obj.iteritems()}


class mixedmethod(object):
    """
    Decorator that allows a method to be both a class method
    and an instance method at the same time.

    Note: To avoid pylint warnings in decorated methods use
          first method argument as a keyword.

    """
    def __init__(self, method):
        self.method = method

    def __get__(self, obj=None, objtype=None):
        @functools.wraps(self.method)
        def method_wrapper(*args, **kwargs):
            if obj is not None:
                return self.method(obj, *args, **kwargs)
            else:
                return self.method(objtype, *args, **kwargs)

        return method_wrapper


def route_path(route_name, request=None, **kwargs):
    """
    Get a route path for an existing route.

    A `DummyRequest` is used when no request is given.

    Returns a String.

    """
    if not request:
        request = DummyRequest()

    return pyramid.url.route_path(route_name, request, **kwargs)


def generate_random_hash(salt='', hash='sha1'):
    """
    Generate a random hash string.

    By default generate a `sha1` hash.

    Other hash can be specified. If so all supported hash
    algorithms are listed in `hashlib.algorithms`.

    Returns a String.

    """
    if hash not in hashlib.algorithms:
        raise Exception('Invalid hash algorithm %s' % hash)

    if isinstance(salt, unicode):
        salt = salt.encode('utf8')

    return generate_hash(os.urandom(48) + salt, hash=hash)


def generate_hash(value, hash='sha1'):
    """
    Generate a hash for a given value.

    By default generate a `sha1` hash.

    Other hash can be specified. If so all supported hash
    algorithms are listed in `hashlib.algorithms`.

    Returns a String.

    """
    sha_obj = getattr(hashlib, hash)(value)
    return sha_obj.hexdigest()


def get_app_namespace(context):
    """
    Get appplication name for a context.

    Sandglass applications are organized under a `sandglass`
    prefix. So all applications module names follow the format::

        sandglass.APP_NAME

    This method returns the `APP_NAME` extracted from the module
    where given context object/class is defined.
    When context is a string it is used as sandglass module name.

    Returns a String.

    """
    if isinstance(context, basestring):
        module_name = context
    else:
        cls = (context if isclass(context) else context.__class__)
        module_name = cls.__module__

    parts = module_name.lower().split('.')
    if len(parts) < 2 or parts[0] != 'sandglass':
        msg = "Context '{ctx}' module '{mod}' is not 'sandglass' namespaced"
        raise Exception(msg.format(ctx=context, mod=module_name))

    # Get the second element in module path
    return parts[1]
