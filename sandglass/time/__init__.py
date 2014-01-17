from pyramid.i18n import TranslationStringFactory
from pyramid.threadlocal import get_current_registry


# String translation function for "sandglass.time" app domain
_ = TranslationStringFactory('sandglass.time')


def get_settings():
    """
    Get application settings.

    Application settings are customized in the ".ini" file.

    Return a Dictionary.

    """
    return get_current_registry().settings


def get_available_languages():
    """
    Get a list with available application languages.

    Return a List of string.

    """
    settings = get_settings()
    return settings['available_languages'].split()
