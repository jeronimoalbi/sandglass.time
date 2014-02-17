import json

from pyramid import response
from pyramid.httpexceptions import HTTPFound


class Response(response.Response):
    """
    Custom sandglass API response.

    """
    content_type = 'application/json'


def error_response(message, data=None):
    """
    Create a JSON error response.

    Extra values can be given using `data` argument.

    Return a Response.

    """
    # TODO: Define error codes for the API and use them in response body
    error_info = {'message': message}
    if data:
        error_info['error'] = data
    else:
        error_info['error'] = True

    body = json.dumps(error_info)
    response = Response(body=body, status_code=500)
    return response


def redirect(url):
    """
    Redirect a request to another URL.

    """
    raise HTTPFound(location=url)
