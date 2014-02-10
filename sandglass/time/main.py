import datetime

from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.renderers import JSON
from sqlalchemy import engine_from_config

from sandglass.time.auth import basic
from sandglass.time.directives import add_rest_resource
from sandglass.time.models import initialize_database


def json_datetime_adapter(obj, request):
    """
    Adapter to properly (de)serialize JSON/Python datetimes.

    """
    # TODO: Add time zone info to dates (See: pytz module)
    # Get a tring representation of the date in ISO 8601 format with TZ
    return obj.strftime('%Y-%m-%dT%H:%M:%S.%f%z')


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
    json_renderer = JSON()
    json_renderer.add_adapter(datetime.datetime, json_datetime_adapter)
    config.add_renderer('json', json_renderer)
    # Authentication support
    acl_auth = ACLAuthorizationPolicy()
    config.set_authorization_policy(acl_auth)
    # Add HTTP basic authentication
    # TODO: Make authentication default when no other auth is on
    basic.initialize_auth(config)
    # Attach sandglass.time to '/time' URL path prefix
    config.include(init_app_modules, route_prefix='time')


def make_wsgi_app(global_config, **settings):
    """
    Create a WSGI application for Sandglass time.

    """
    config = Configurator(settings=settings)
    config.include('sandglass.time')
    return config.make_wsgi_app()
