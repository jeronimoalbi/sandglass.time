"""
Request module

Extending the request objects with utility functions.

"""
import logging

from pyramid.events import NewRequest
from pyramid.security import authenticated_userid
from sqlalchemy.orm import joinedload

from sandglass.time.models.user import User
from sandglass.time.resource.utils import REQUEST_METHODS
from sandglass.time.utils import get_settings

LOG = logging.getLogger(__name__)


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


def authenticated_user(request):
    """
    Get authenticated user object.

    Returns a User.

    """
    user = None
    token = authenticated_userid(request)
    query = User.query().filter(User.token == token)
    query = query.options(
        joinedload('groups').joinedload('permissions')
    )
    try:
        user = query.first()
    except:
        LOG.exception("Unable to get authenticated user")

    return user


def add_cors_headers_response_callback(event):
    """
    Event callback to add C.O.R.S. HTTP headers to each response.

    """
    def cors_headers_callback(request, response):
        if request.matched_route is None:
            return

        request_methods = REQUEST_METHODS + ('OPTIONS', )
        response.headers.update({
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': ', '.join(request_methods),
            # TODO: Implement support for custom CORS headers
            'Access-Control-Allow-Headers': 'Authorization, Content-Type',
            'Access-Control-Allow-Credentials': 'true',
            'Access-Control-Max-Age': '1728000',
        })

    event.request.add_response_callback(cors_headers_callback)


def extend_request_object(config):
    """
    Add extra methods to request objects.

    """
    settings = config.registry.settings
    if settings.get('response.enable_cors_headers', 'false') == 'true':
        config.add_subscriber(add_cors_headers_response_callback, NewRequest)

    config.add_request_method(callable=is_member, reify=True)
    config.add_request_method(callable=is_collection, reify=True)
    config.add_request_method(callable=rest_collection_mode, reify=True)
    config.add_request_method(callable=authenticated_user, reify=True)
