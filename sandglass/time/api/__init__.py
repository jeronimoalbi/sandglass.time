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
