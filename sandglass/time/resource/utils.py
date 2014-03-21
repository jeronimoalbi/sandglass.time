from functools import wraps

from pyramid.httpexceptions import HTTPMethodNotAllowed

# Request methods supported by APi resources
REQUEST_METHODS = ('GET', 'POST', 'PUT', 'DELETE')


def allow_request_methods(methods):
    """
    Resource method decorator to allow specific request method(s).

    HTTP method not allowed is raised when request uses a method
    that is not in the allowed methods list.

    """
    if isinstance(methods, basestring):
        allowed_methods = [methods]
    else:
        allowed_methods = methods

    def decorator(func):
        @wraps(func)
        def allow_request_methods_wrapper(context, request):
            if request.method not in allowed_methods:
                raise HTTPMethodNotAllowed()

            return func(context, request)

        return allow_request_methods_wrapper

    return decorator
