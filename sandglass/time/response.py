import json

from pyramid import response


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
    error_info = {'message': message}
    if data:
        error_info['error'] = data

    body = json.dumps(error_info)
    response = Response(body=body, status_code=500)
    return response
