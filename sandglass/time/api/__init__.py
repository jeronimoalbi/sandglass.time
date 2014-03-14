import logging

LOG = logging.getLogger(__name__)


class ApiManager(object):
    """
    Manager for API versions.

    """
    def __init__(self, versions):
        self.registry = {version: {} for version in versions}

    def register(self, version, resource):
        """
        Register a `BaseResource` for an API version.

        Returns a Boolean.

        """
        if version not in self.registry:
            LOG.error("Invalid API version %s", version)
            return False

        self.registry[version][resource.name] = resource
        return True

    def get_versions(self):
        """
        Get a list of API versions.

        Returns a List of strings.

        """
        return self.registry.keys()

    def get_resources(self, version):
        """
        Get all registered API resources by version.

        Returns a List of BaseResource.

        """
        return self.registry[version].values()


# Global API manager
API = ApiManager(versions=('v1', ))


def include_api_versions(config):
    """
    Initialize all supported API versions.

    """
    for version in API.get_versions():
        # Scan the API forder for current version to register resources
        path = 'sandglass.time.api.{}'.format(version)
        config.scan(path)
        # Load current API version
        config.include(path, route_prefix=version)
