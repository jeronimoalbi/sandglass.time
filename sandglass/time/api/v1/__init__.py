from sandglass.time.api import add_api_resource_describe
from sandglass.time.api import API
from sandglass.time.api import ApiDescribeResource
from sandglass.time.resource import add_api_rest_routes


class ApiV1DescribeResource(ApiDescribeResource):
    """
    Resource to describe API version 1.

    """
    version = "v1"

    def describe(self):
        resource_info_list = []
        for resource in self.resources:
            path = resource.get_collection_path()
            resource_info = {
                'name': resource.name,
                'path': path,
                'describe': "{}@describe".format(path),
                'doc': (resource.__doc__.strip() if resource.__doc__ else ''),
            }
            resource_info_list.append(resource_info)

        data = {
            'version': self.version,
            'resources': resource_info_list,
        }

        return data


def includeme(config):
    """
    Load API version 1 resources.

    """
    # API version must be the last item in route_prefix
    version = config.route_prefix.split('/')[-1]

    # Add support for describing resources in current API
    add_api_resource_describe(config, version, ApiV1DescribeResource)

    # Load API REST routes for current config path
    add_api_rest_routes(config)

    # Attach resources to API REST routes
    for resource in API.get_resources(version):
        config.add_rest_resource(resource)
