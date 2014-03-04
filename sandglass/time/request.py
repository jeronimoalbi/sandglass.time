"""
Request module

Extending the request objects with utility functions.

"""
from sandglass.time.utils import get_settings


def is_member(request):
    """
    Check if current request body contains member data.

    Returns a Boolean.

    """
    body = (request.json_body if request.is_body_readable else None)
    return isinstance(body, dict)


def is_collection(request):
    """
    Check if current request body contains collection data.

    Returns a Boolean.

    """
    body = (request.json_body if request.is_body_readable else None)
    return isinstance(body, list)


def rest_collection_mode(request):
    """
    Get current request REST mode used for collection.

    Mode is given as an HTTP header `X-REST-Collection-Mode`.

    Valid values:
      - permissive: Allow POSTing object, Allow returning object.
      - strict: Only allow POSTing and retuning of collections.

    Returns a String.

    """
    valid_modes = ('permissive', 'strict')
    mode = request.headers.get('X-REST-Collection-Mode')
    if mode not in valid_modes:
        # Get default mode from application settings
        settings = get_settings()
        mode = settings.get('request.rest_collection_mode')
        if mode not in valid_modes:
            mode = 'strict'

    return mode


def extend_request_object(config):
    """
    Add extra methods to request objects.

    """
    config.add_request_method(callable=is_member, reify=True)
    config.add_request_method(callable=is_collection, reify=True)
    config.add_request_method(callable=rest_collection_mode, reify=True)
