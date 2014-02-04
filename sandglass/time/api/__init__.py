import logging

from functools import wraps

from pyramid.decorator import reify
from pyramid.exceptions import NotFound
from pyramid.httpexceptions import HTTPMethodNotAllowed

from sandglass.time.utils import route_path

LOG = logging.getLogger(__name__)


# TODO: Add include related for member=True
def rpc(member=False, method=None, permissions=None, **kwargs):
    """
    Mark decorated method to be accesible by RPC calls.

    When `member` is True handler receives an argument with the requested
    member PK (or object instance).

    By default all RPC request methods are supported, but a method name
    can be given using `method` argument.

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
            'is_member_call': member,
            'permissions': permissions,
            'method': method,
        })

        return rpc_wrapper_inner

    return rpc_wrapper


class APIRequestDataError(Exception):
    """
    Exception for invalid API requests.

    API requests uses JSON format to transfer data. This exception
    is raised when data has an invalid format and fails during
    JSON serialization.

    """


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

    @classmethod
    def get_collection_path(cls):
        """
        Get collection URL path.

        Return a String.

        """
        prefix = cls.get_route_prefix()
        route_name = "{}_collection".format(prefix)
        return route_path(route_name)

    @classmethod
    def get_member_path(cls, pk):
        """
        Get member URL path.

        Argument `pk` is the primary key value for the member object.

        Return a String.

        """
        prefix = cls.get_route_prefix()
        route_name = "{}_member".format(prefix)
        return route_path(route_name, pk=pk)

    @classmethod
    def get_related_path(cls, pk, related_name):
        """
        Get member URL path.

        Argument `pk` is the primary key value for the member object,
        and `related_name` is the name of the related object(s).


        Return a String.

        """
        prefix = cls.get_route_prefix()
        route_name = "{}_related".format(prefix)
        return route_path(route_name, pk=pk, related_name=related_name)

    def __init__(self, request):
        self.request = request

    def _get_pk_value(self):
        value = self.request.matchdict.get('pk')
        try:
            pk_value = int(value)
        except (ValueError, TypeError):
            pk_value = None

        return pk_value

    def _get_related_name(self):
        related_name = self.request.matchdict.get('related_name')
        # Check that related name is in fact a relationship
        if related_name not in self.model.__mapper__.relationships:
            raise NotFound()

        return related_name

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
    def request_data(self):
        """
        Get JSON data from current request body.

        """
        try:
            return self.request.json_body
        except ValueError:
            LOG.exception('Invalid JSON in request body')
            raise APIRequestDataError()

    @reify
    def pk_value(self):
        """
        Get primary key value for current request.

        Return an Integer or None.

        """
        return self._get_pk_value()

    @reify
    def related_name(self):
        """
        Get related name when it is available in the URL.

        When no related name is given or the name is not a model
        relationship `NotFound` is raised.

        Return a String.

        """
        return self._get_related_name()

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
        # When an RPC call is done for an object use its PK as argument
        if self.pk_value:
            return self.rpc_handler(self.pk_value)
        else:
            # When RPC is called for a collection dont use arguments
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
