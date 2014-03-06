# pylint: disable=W0622

import inspect
import logging

import dateutil.parser

from pyramid.decorator import reify
from pyramid.exceptions import NotFound

from sandglass.time.utils import route_path

LOG = logging.getLogger(__name__)

REQUEST_METHODS = ('GET', 'POST', 'PUT', 'DELETE')

REST_ROUTE_INFO = {
    # GET: List all items
    # POST: Create new item(s)
    # PUT: Update item(s)
    # DELETE: Delete all items
    'collection': {
        'route_name': 'api.rest.collection',
        'pattern': r'/{member}/',
        'methods': REQUEST_METHODS,
        # Note: Require `resource_action_predicate` during view attachment
        'action': {
            'pattern': r'/{member}/@{action}',
            # All request methods are supported
            'methods': REQUEST_METHODS,
        },
    },
    # GET: Get a single item
    # PUT: Update a single item
    # DELETE: Delete a single item
    'member': {
        'route_name': 'api.rest.member',
        'pattern': r'/{member}/{pk:\d+}/',
        'methods': ('GET', 'PUT', 'DELETE'),
        # Note: Require `resource_action_predicate` during view attachment
        'action': {
            'pattern': r'/{member}/{pk:\d+}/@{action}',
            # All request methods are supported
            'methods': REQUEST_METHODS,
        },
    },
    # GET: List all related items
    # DELETE: Delete related item(s)
    'related': {
        'route_name': 'api.rest.related',
        'pattern': r'/{member}/{pk:\d+}/{related_name}/',
        'methods': ('GET', 'DELETE'),
    },
}


def add_action_info(func, name=None, type='*', permission=None, methods=None,
                    extra=None):
    """
    Add API action info to a method.

    """
    if type not in ('*', 'member', 'collection'):
        raise Exception("Invalid resource action type %s" % type)

    # Save action related info
    func.__action__ = {
        'request_method': methods or REQUEST_METHODS,
        'attr_name': func.__name__,
        'name': name or func.__name__.replace('_', '-'),
        'permission': permission,
        'type': type,
        'extra': extra,
    }

    return func


def member_action(name=None, permission=None, methods=None):
    """
    Mark decorated method to be accesible as an action.

    #TODO: Document arguments.

    """
    def inner_member_action(func):
        return add_action_info(func, name=name, type='member',
                               permission=permission, methods=methods)

    return inner_member_action


def collection_action(name=None, permission=None, methods=None):
    """
    Mark decorated method to be accesible as an action.

    #TODO: Document arguments.

    """
    def inner_collection_action(func):
        return add_action_info(func, name=name, type='collection',
                               permission=permission, methods=methods)

    return inner_collection_action


def action(name=None, permission=None, methods=None):
    """
    Mark decorated method to be accesible as an action.

    #TODO: Document arguments.

    """
    def inner_action(func):
        return add_action_info(func, name=name, permission=permission,
                               methods=methods)

    return inner_action


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
        route_info = REST_ROUTE_INFO['collection']
        route_name = route_info['route_name']
        member = cls.get_route_prefix()
        return route_path(route_name, member=member)

    @classmethod
    def get_member_path(cls, pk):
        """
        Get member URL path.

        Argument `pk` is the primary key value for the member object.

        Return a String.

        """
        route_info = REST_ROUTE_INFO['member']
        route_name = route_info['route_name']
        member = cls.get_route_prefix()
        return route_path(route_name, member=member, pk=pk)

    @classmethod
    def get_related_path(cls, pk, related_name):
        """
        Get member URL path.

        Argument `pk` is the primary key value for the member object,
        and `related_name` is the name of the related object(s).

        Return a String.

        """
        route_info = REST_ROUTE_INFO['related']
        route_name = route_info['route_name']
        member = cls.get_route_prefix()
        return route_path(
            route_name,
            member=member,
            pk=pk,
            related_name=related_name)

    @classmethod
    def get_actions_by_type(cls, action_type):
        """
        Get the list of action information for current class.

        Action type can be member, collection or * for any type.

        Return a List of dictionaries.

        """
        action_info_list = []
        member_list = inspect.getmembers(cls, predicate=inspect.ismethod)
        for member in member_list:
            # Get action info from the method definition
            action_info = getattr(member[1], '__action__', None)
            if not action_info:
                continue

            # Check if current action info match action type
            if action_type != '*':
                if action_info.get('type') != action_type:
                    # Skip current action info when type is not right
                    continue

            action_info_list.append(action_info)

        return action_info_list

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
        return self.request.matchdict.get('related_name')

    @property
    def is_member_request(self):
        """
        Check if current request is a member request.

        Method checks if pk_value is not None. When no pk value is
        available it means the current is a collection request.

        Return a Boolean.

        """
        return self.pk_value is not None

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

    def get_filter_from_to(self):
        """
        Get from/to request arguments as python dates.

        ValueError is raised when date format is invalid for one
        or both dates.

        Return a Tuple.

        """
        from_date = self.request.params.get('from')
        if from_date:
            # Convert string to date
            from_date = dateutil.parser.parse(from_date)

        to_date = self.request.params.get('to')
        if to_date:
            # Convert string to date
            to_date = dateutil.parser.parse(to_date)

        return (from_date, to_date)


class RootModelFactory(object):
    """
    Root factory that uses current request model class as context.

    Model class is getted from current request resource.

    """
    def __init__(self):
        from sandglass.time.directives import RESOURCE_REGISTRY
        self.resources = RESOURCE_REGISTRY

    def __call__(self, request):
        return self

    def __getitem__(self, name):
        if name not in self.resources:
            return

        # Use current resource model as context
        return self.resources[name].model


def add_api_rest_routes(config):
    """
    Add API REST routes to a config object.

    """
    for route_info in REST_ROUTE_INFO.values():
        name = route_info['route_name']
        pattern = route_info['pattern']
        methods = route_info['methods']
        config.add_route(
            name,
            pattern=pattern,
            request_method=methods,
            factory=RootModelFactory(),
            traverse="/{member}")

        #Get action information for current route
        action_info = route_info.get('action')
        if not action_info:
            continue

        # Add action route when available
        action_name = "{}_action".format(name)
        action_pattern = action_info['pattern']
        action_methods = action_info['methods']
        config.add_route(
            action_name,
            pattern=action_pattern,
            request_method=action_methods,
            factory=RootModelFactory(),
            traverse="/{member}")


def load_api_v1(config):
    """
    Load API version 1 resources.

    """
    # Load API REST routes for current config path
    add_api_rest_routes(config)

    # Attach resources to API REST routes
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


def include_api_versions(config):
    """
    Initialize all supported API versions.

    """
    config.scan('sandglass.time.api.v1')
    config.include(load_api_v1, route_prefix='v1')
