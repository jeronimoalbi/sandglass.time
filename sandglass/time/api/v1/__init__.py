from sandglass.time.api import API
from sandglass.time.resource import add_api_rest_routes


def includeme(config):
    """
    Load API version 1 resources.

    """
    # Load API REST routes for current config path
    add_api_rest_routes(config)

    # API version must be the last item in route_prefix
    version = config.route_prefix.split('/')[-1]

    # Attach resources to API REST routes
    for resource in API.get_resources(version):
        config.add_rest_resource(resource)
