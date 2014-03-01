"""
Request module

Extending the request objects with utility functions.

"""


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


def extend_request_object(config):
    """
    Add extra methods to request objects.

    """
    default_kwargs = {'property': False, 'reify': True}
    config.add_request_method(callable=is_member, **default_kwargs)
    config.add_request_method(callable=is_collection, **default_kwargs)
