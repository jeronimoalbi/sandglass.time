"""
Request module

Extending the request objects with utility functions

"""


def is_member(request):
    if request.is_body_readable:
        return isinstance(request.json_body, dict)


def is_collection(request):
    if request.is_body_readable:
        return isinstance(request.json_body, list)


def is_empty(request):
    if (request.is_body_readable and 
        (request.is_collection or request.is_member)):
        return len(request.json_body) == 0


def extend_request_object(config):
    """
    Add extension methods to request object
    """
    config.add_request_method(callable=is_member, property=False, reify=True)
    config.add_request_method(
        callable=is_collection, property=False, reify=True)
    config.add_request_method(callable=is_empty, property=False, reify=True)
