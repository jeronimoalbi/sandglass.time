from pyramid.config import Configurator


def make_wsgi_app(global_config, **settings):
    """
    Create a WSGI application for Sandglass time.

    """
    config = Configurator(settings=settings)
    config.include('sandglass.time.config')
    return config.make_wsgi_app()
