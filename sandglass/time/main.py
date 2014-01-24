from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from sandglass.time.directives import add_rest_resource
from sandglass.time.models import initialize_database


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
    config.include("sandglass.time.api.init_api_versions", route_prefix='api')


def prepare_application(config):
    """
    Prepare sandglass.time application.

    """
    config.add_translation_dirs('sandglass.time:locales/')
    config.add_directive('add_rest_resource', add_rest_resource)
    config.include(init_app_modules, route_prefix='time')


def run_wsgi(global_config, **settings):
    """
    Main Sandglass time application entry point.

    """
    config = Configurator(settings=settings)
    config.include('pyramid_tm')
    config.include('pyramid_mailer')
    prepare_application(config)
    init_database(settings)

    return config.make_wsgi_app()
