from pyramid.exceptions import NotFound


def rpc(permissions=None):
    """
    Mark decorated method to be accesible by RPC calls.

    """
    def rpc_wrapper(func):
        # TODO: Implement permissions
        func.__rpc__ = {}
        return func

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

    def handle_rpc_call(self):
        """
        Main entry point for API RPC calls.

        API RPC calls are triggered when a request has the `call` parameter
        available in the request.

        To publish a method to be accesible as RCP call decorate it using
        the `@rpc` decorator.

        """
        call_name = self.request.params.get('call')
        rpc_handler = (getattr(self, call_name, None) if call_name else None)
        if not hasattr(rpc_handler, '__rpc__'):
            raise NotFound()

        return rpc_handler()


def load_api_v1(config):
    """
    Load API version 1 resources.

    """
    resources = (
        'user.UserResource',
    )
    for name in resources:
        config.add_rest_resource('sandglass.time.api.v1.' + name)


def init_api_versions(config):
    """
    Initialize all supported API versions.

    """
    config.include(load_api_v1, route_prefix='v1')
