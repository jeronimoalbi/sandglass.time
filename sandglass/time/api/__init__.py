from functools import wraps

from pyramid.decorator import reify
from pyramid.exceptions import NotFound
from pyramid.httpexceptions import HTTPMethodNotAllowed


def rpc(permissions=None, method=None, **kwargs):
    """
    Mark decorated method to be accesible by RPC calls.

    """
    def rpc_wrapper(func):
        @wraps(func)
        def rpc_wrapper_inner(self, *args, **kwargs):
            # When a request method is given check request before call
            if method:
                if method.upper() != self.request.method:
                    raise HTTPMethodNotAllowed()

            return func(self, *args, **kwargs)

        rpc_wrapper_inner.__rpc_func__ = func
        # Save RPC related info inside wrapped function/method
        func.__rpc__ = kwargs.copy()
        func.__rpc__.update({
            'permissions': permissions,
            'method': method,
        })

        return rpc_wrapper_inner

    return rpc_wrapper


class BaseResource(object):
    """
    Base class for Sandglass time API resources.

    """
    # Name used as prefix for this resource URLs
    # NOTE: For REST APIs it is recommended to be in plural form
    name = None

    @classmethod
    def get_route_prefix(cls):
        """
        Get prefix to be used for current resource URL path.

        Returns a String.

        """
        if not cls.name:
            raise Exception("Resource name can't be empty")

        return cls.name.lower()

    def __init__(self, request):
        self.request = request

    def _get_rpc_handler(self):
        # Get the method that handles current RPC request
        call_name = self.request.params.get('call')
        rpc_handler = None
        if call_name:
            rpc_handler = getattr(self, call_name, None)

        # TODO: Handle permissions for each request
        if not hasattr(rpc_handler, '__rpc_func__'):
            raise NotFound()

        return rpc_handler

    @reify
    def rpc_handler(self):
        """
        Get the method that handles current RPC call.

        """
        return self._get_rpc_handler()

    def handle_rpc_call(self):
        """
        Main entry point for API RPC calls.

        API RPC calls are triggered when a request has the `call` parameter
        available in the request; Value for this parameter is the name of
        method that should handle the request.

        To publish a method to be accesible as RCP call decorate it using
        the `@rpc` decorator.

        """
        return self.rpc_handler()


def load_api_v1(config):
    """
    Load API version 1 resources.

    """
    resources = (
        'activity.ActivityResource',
        'client.ClientResource',
        'project.ProjectResource',
        'tag.TagResource',
        'task.TaskResource',
        'user.UserResource',
    )
    for name in resources:
        config.add_rest_resource('sandglass.time.api.v1.' + name)


def init_api_versions(config):
    """
    Initialize all supported API versions.

    """
    config.scan('sandglass.time.api.v1')
    config.include(load_api_v1, route_prefix='v1')
