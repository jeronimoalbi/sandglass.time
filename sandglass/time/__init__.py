import os

from pkg_resources import require

from pyramid.i18n import TranslationStringFactory

from sandglass.time.utils import get_settings


# String translation function for "sandglass.time" app domain
_ = TranslationStringFactory('sandglass.time')


def guess_version(app_name, file_name):
    """
    Get current application version.

    Version can be successfuly getted when app is installed, and is being
    imported from the installed directory (not from current location).

    """
    version = '(not installed)'
    try:
        info = require(app_name)[0]
        base_path = os.path.dirname(file_name)
        base_path = os.path.dirname(base_path)
        #for applications with namespace we need to dig one more level
        if '.' in app_name:
            base_path = os.path.dirname(base_path)

        if base_path == info.location:
            version = info.version
    except:
        pass

    return version


def get_available_languages():
    """
    Get a list with available application languages.

    Return a List of string.

    """
    settings = get_settings()
    return settings['available_languages'].split()


def includeme(config):
    """
    Default Sandglass time application initialization function.

    Pyramid uses this function as entry point for `sandglass.time`.

    """
    import sandglass.time.main

    # Init application dependencies
    config.include('pyramid_tm')
    config.include('pyramid_mailer')
    # Prepare application and initialize database
    sandglass.time.main.prepare_application(config)
    sandglass.time.main.init_database(config.registry.settings)


__version__ = guess_version('sandglass.time', __file__)
