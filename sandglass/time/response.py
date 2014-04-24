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
    error_info = {
        'message': message,
        'error': (data if data is not None else True),
    }
    body = json.dumps(error_info)
    return Response(body=body, status_code=500)


def info_response(message, data=None):
    """
    Create a JSON info response.

    Extra values can be given using `data` argument.

    Return a Response.

    """
    info = {
        'message': message,
        'info': (data if data is not None else True),
    }
    body = json.dumps(info)
    return Response(body=body, status_code=200)


def redirect(url):
    """
    Redirect a request to another URL.

    """
    raise HTTPFound(location=url)
