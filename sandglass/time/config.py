import datetime

import pytz

from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.renderers import JSONP
from sqlalchemy import engine_from_config

from sandglass.time.api import include_api_versions
from sandglass.time.auth.basic import setup_basic_http_auth
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


def include_resources(config):
    """
    Initialize `sandglass.time` application resources.

    """
    config.include(include_api_versions, route_prefix='api')


def configure_application(config):
    """
    Configure `sandglass.time` application.

    """
    config.add_translation_dirs('sandglass.time:locales/')
    config.add_directive('add_rest_resource', add_rest_resource)

    json_renderer = JSONP(param_name='callback')
    json_renderer.add_adapter(datetime.datetime, json_datetime_adapter)
    config.add_renderer('json', json_renderer)

    # Add custom request methods
    extend_request_object(config)

    # Scan modules that need to be pre-loaded
    config.scan('sandglass.time.models')
    config.scan('sandglass.time.errorhandlers')

    # Attach sandglass.time resources to '/time' URL path prefix
    config.include(include_resources, route_prefix='time')


def include_authentication(config):
    """
    Setup user authentication and ACL authorization.

    """
    acl_auth = ACLAuthorizationPolicy()
    config.set_authorization_policy(acl_auth)
    # TODO: Get authentication method from settings
    setup_basic_http_auth(config)


def include_dependencies(config):
    """
    Include external application dependencies.

    """
    config.include('pyramid_tm')
    config.include('pyramid_mailer')


def configure_database(config):
    """
    Create/update database with all sandglass models.

    Models has to be registered before calling this function.

    """
    settings = config.registry.settings
    engine = engine_from_config(settings, prefix='database.')
    initialize_database(engine)


def includeme(config):
    """
    Default Sandglass time application initialization function.

    Pyramid uses this function as entry point for `sandglass.time`.

    """
    include_dependencies(config)
    include_authentication(config)
    configure_application(config)
    configure_database(config)
