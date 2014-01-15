from pyramid.config import Configurator


def run_wsgi(global_config, **settings):
    """
    Main Sandglass time application entry point.

    """
    config = Configurator(settings=settings)
    config.include("cornice")
    config.scan("sandglass.time.views")

    return config.make_wsgi_app()
