# pylint: disable=W0613
import logging

from pyramid.path import DottedNameResolver

from sandglass.time.resource.utils import allow_request_methods

from .registry import register_resource
from .registry import RESOURCE_REGISTRY
from .utils import REQUEST_METHODS

LOG = logging.getLogger(__name__)

# Permission suffix by request method
PERMISSION_SUFFIX = {
    'POST': 'create',
    'GET': 'read',
    'PUT': 'update',
    'DELETE': 'delete',
}

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
    # PUT: Append related item(s)
    # DELETE: Delete related item(s)
    'related': {
        'route_name': 'api.rest.related',
        'pattern': r'/{member}/{pk:\d+}/{related_name}/',
        'methods': ('GET', 'PUT', 'DELETE'),
    },
}


class RootModelFactory(object):
    """
    Root factory that uses current request model class as context.

    Model class is getted from current request resource.

    """
    def __init__(self):
        self.resources = RESOURCE_REGISTRY

    def __call__(self, request):
        return self

    def __getitem__(self, name):
        if name not in self.resources:
            return

        # Use current resource model as context
        return self.resources[name].model


def resource_action_predicate(action_name):
    """
    Function to define a view predicate for action views.

    Return a Function.

    """
    def predicate(context, request):
        current_action_name = request.matchdict.get('action')
        if current_action_name == action_name:
            return True

        # Check for URL action name mismatch
        if action_name == current_action_name.replace('_', '-'):
            msg = u"Invalid action name '@{}'. Try using '@{}'.".format(
                current_action_name,
                action_name,
            )
            LOG.warning(msg)

        return False

    return predicate


def add_rest_resource(config, cls_or_dotted):
    """
    Add routes and views for a `RestResource` class.

    """
    # Get the resource class definition
    resolver = DottedNameResolver()
    cls = resolver.maybe_resolve(cls_or_dotted)
    resource_name = cls.get_route_prefix()
    register_resource(cls)

    # Generate routes and attach views for current class
    for route_type, route_info in REST_ROUTE_INFO.items():
        match_param = "member={}".format(resource_name)

        # Get action names for current route type and initialize
        # a route predicate to match the names
        if 'action' in route_info:
            action_info_list = cls.get_actions_by_type(route_type)
            # Attach action methods to current route
            for action_info in action_info_list:
                action_name = action_info['name']
                request_method = action_info['request_method']

                # Init permission for action calls
                permission_name = action_info.get('permission')
                if permission_name:
                    permission = permission_name
                else:
                    permission = cls.model.get_permission('action')

                # Create a resource action predicate to call the view
                # only when current action name is called in the URL
                custom_predicates = (resource_action_predicate(action_name), )
                # Add a view also for implicit action call
                config.add_view(
                    cls,
                    attr=action_info['attr_name'],
                    match_param=match_param,
                    route_name="{}_action".format(route_info['route_name']),
                    decorator=allow_request_methods(request_method),
                    custom_predicates=custom_predicates,
                    renderer='json',
                    request_method=REQUEST_METHODS,
                    permission=permission)

        # Add views to handle different request methods in this view
        for request_method in route_info['methods']:
            # Init the name of the methos that the class should
            # implement to handle requests for current request method
            attr_name = '{0}_{1}'.format(request_method.lower(), route_type)
            view_handler = getattr(cls, attr_name, None)
            # Skip non callable attributes
            if not hasattr(view_handler, '__call__'):
                continue

            # Init permission name for current handler
            permission_name = PERMISSION_SUFFIX[request_method]
            permission = cls.model.get_permission(permission_name)

            config.add_view(
                cls,
                attr=attr_name,
                match_param=match_param,
                route_name=route_info['route_name'],
                renderer='json',
                request_method=request_method,
                permission=permission)


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
