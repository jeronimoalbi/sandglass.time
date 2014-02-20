# pylint: disable=W0613

from functools import wraps

from pyramid.httpexceptions import HTTPMethodNotAllowed
from pyramid.path import DottedNameResolver

from sandglass.time.api import REQUEST_METHODS
from sandglass.time.api import REST_ROUTE_INFO


# Added REST API resources are saved here
RESOURCE_REGISTRY = {}

# Permission suffix by request method
PERMISSION_SUFFIX = {
    'POST': 'create',
    'GET': 'read',
    'PUT': 'update',
    'DELETE': 'delete',
}


def resource_action_predicate(action_name):
    """
    Function to define a view predicate for action views.

    Return a Function.

    """
    def predicate(context, request):
        return request.matchdict.get('action') == action_name

    return predicate


def allow_request_methods(methods):
    """
    Resource method decorator to allow specific request method(s).

    HTTP method not allowed is raised when request uses a method
    that is not in the allowed methods list.

    """
    if isinstance(methods, basestring):
        allowed_methods = [methods]
    else:
        allowed_methods = methods

    def decorator(func):
        @wraps(func)
        def allow_request_methods_wrapper(context, request):
            if request.method not in allowed_methods:
                raise HTTPMethodNotAllowed()

            return func(context, request)

        return allow_request_methods_wrapper

    return decorator


def add_rest_resource(config, cls_or_dotted):
    """
    Add routes and views for a `RestResource` class.

    """
    # Get the resource class definition
    resolver = DottedNameResolver()
    cls = resolver.maybe_resolve(cls_or_dotted)
    resource_name = cls.get_route_prefix()
    RESOURCE_REGISTRY[resource_name] = cls

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
