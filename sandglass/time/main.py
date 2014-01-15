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


def run_wsgi(global_config, **settings):
    """
    Main Sandglass time application entry point.

    """
    config = Configurator(settings=settings)
    prepare_database(config, settings)
    config.include("cornice")
    config.scan("sandglass.time.views")

    return config.make_wsgi_app()
