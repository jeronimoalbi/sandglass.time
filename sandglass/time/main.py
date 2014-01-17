from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from sandglass.time.models import initialize_database


def prepare_database(config, settings):
    """
    TODO

    """
    config.scan('sandglass.time.models')
    engine = engine_from_config(settings, prefix='database.')
    initialize_database(engine)


def prepare_application(config):
    """
    TODO

    """
    config.include("cornice")
    config.add_translation_dirs('sandglass.time:locales/')
    config.scan("sandglass.time.views")
    config.scan("sandglass.time.api.resources")


def run_wsgi(global_config, **settings):
    """
    Main Sandglass time application entry point.

    """
    config = Configurator(settings=settings)
    config.include('pyramid_tm')
    config.include('pyramid_mailer')
    prepare_database(config, settings)
    prepare_application(config)

    return config.make_wsgi_app()
