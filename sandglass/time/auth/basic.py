from pyramid.authentication import BasicAuthAuthenticationPolicy
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPUnauthorized
from pyramid.security import forget

from sandglass.time.models.user import User


def handle_basic_auth_challenge(request):
    """
    Handle HTTPForbidden errors for HTTP Basic Auth.

    Return a response to challenge remote "browser" for a
    user name and password.

    """
    if request.is_xhr:
        response = HTTPForbidden()
    else:
        response = HTTPUnauthorized()

    response.headers.update(forget(request))
    return response


def auth_callback(username, password, request):
    """
    HTTP standard basic authentication protocol callback.

    Return None if the user doesn't exist or a sequence of principal
    identifiers (possibly empty) if the user does exist.

    """
    user = User.get_by_token(username)
    authenticated = (user and user.key == password)
    if not authenticated:
        return

    # Get user credentials
    return [unicode(group) for group in user.groups]


def initialize_auth(config):
    """
    Initialize HTTP Basic Auth support.

    """
    realm = "Sandglass API"
    basic_auth = BasicAuthAuthenticationPolicy(auth_callback, realm=realm)
    config.set_authentication_policy(basic_auth)
    config.add_forbidden_view(handle_basic_auth_challenge)
