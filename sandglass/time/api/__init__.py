class BaseResource(object):
    """
    Base class for Sandglass time API resources.

    """
    # Name used as prefix for this resource URLs
    name = None

    @classmethod
    def get_route_prefix(cls):
        """
        """
        name = cls.name
        # When no name is assigned use class name as resource name
        if name is None:
            name = cls.__name__.replace('Resource', '')

        return name.lower()

    def __init__(self, request):
        self.request = request


class RestResource(BaseResource):
    """
    Base REST API resource class.

    """
    def get_all(self, *args, **kwargs):
        return {}


def load_api_v1(config):
    """
    Load API version 1 resources.

    """
    # TODO: Resolve and load classes dinamically from a dotted string
    from sandglass.time.api.v1.user import UserResource

    config.add_api_resource(UserResource)


def load_api_versions(config):
    """
    TODO

    """
    config.include(load_api_v1, route_prefix='v1')


def load_resources(config):
    """
    TODO

    """
    config.include(load_api_versions, route_prefix='api')
