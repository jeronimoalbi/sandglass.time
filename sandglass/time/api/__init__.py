import logging

from pyramid.security import ALL_PERMISSIONS
from pyramid.security import Allow
from pyramid.security import Authenticated
from pyramid.security import Deny
from pyramid.security import Everyone
from zope import interface

from sandglass.time.interfaces import IDescribable
from sandglass.time.security import Administrators

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

    def is_valid_version(self, version):
        """
        Check if an API version is valid.

        Returns a Boolean.

        """
        return version in self.registry


# Global API manager
API = ApiManager(versions=('v1', ))


class ApiDescribeResource(object):
    """
    Base resource to describe API resources.

    """
    interface.implements(IDescribable)

    # Version to describe
    version = None

    @property
    def __acl__(self):
        return [
            (Allow, Authenticated, ALL_PERMISSIONS),
            (Allow, Administrators, ALL_PERMISSIONS),
            (Deny, Everyone, ALL_PERMISSIONS),
        ]

    def __init__(self, request):
        if not API.is_valid_version(self.version):
            msg = "API version {} is not valid".format(self.version)
            raise Exception(msg)

        self.request = request

    def __call__(self):
        return self.describe()

    @property
    def resources(self):
        return API.get_resources(self.version)

    def describe(self):
        raise NotImplementedError()


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
