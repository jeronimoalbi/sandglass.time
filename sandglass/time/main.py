import datetime

import pytz

from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.renderers import JSONP
from sqlalchemy import engine_from_config

from sandglass.time.auth import basic
from sandglass.time.directives import add_rest_resource
from sandglass.time.models import initialize_database
from sandglass.time.request import extend_request_object


def json_datetime_adapter(obj, request):
    """
    Adapter to properly serialize datetimes to ISO8601.

    Return a String.

    """
    if obj.tzinfo is None:
        # We only use UTC datetimes
        tzinfo = pytz.timezone("UTC")
        obj = obj.replace(tzinfo=tzinfo)

    # Get a tring representation of the date in ISO 8601 format with TZ
    return obj.isoformat()


def init_database(settings):
    """
    Create/update database with all sandglass models.

    Models has to be registered before calling this function.

    """
    engine = engine_from_config(settings, prefix='database.')
    initialize_database(engine)


def init_app_modules(config):
    """
    Initialize application modules.

    """
    config.scan('sandglass.time.models')
    config.scan('sandglass.time.errorhandlers')
    config.include("sandglass.time.api.init_api_versions", route_prefix='api')


def prepare_application(config):
    """
    Prepare sandglass.time application.

    """
    config.add_translation_dirs('sandglass.time:locales/')
    config.add_directive('add_rest_resource', add_rest_resource)
    # Add a renderer for dates in JSON (de)serialization
    json_renderer = JSONP(param_name='callback')
    json_renderer.add_adapter(datetime.datetime, json_datetime_adapter)
    config.add_renderer('json', json_renderer)

    # Authentication support
    acl_auth = ACLAuthorizationPolicy()
    config.set_authorization_policy(acl_auth)
    # Add HTTP basic authentication
    # TODO: Make authentication default when no other auth is on
    basic.initialize_auth(config)

    # Add custom request methods
    extend_request_object(config)

    # Attach sandglass.time to '/time' URL path prefix
    config.include(init_app_modules, route_prefix='time')


def make_wsgi_app(global_config, **settings):
    """
    Create a WSGI application for Sandglass time.

    """
    config = Configurator(settings=settings)
    config.include('sandglass.time')
    return config.make_wsgi_app()
