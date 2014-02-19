import inspect

from pyramid.path import DottedNameResolver

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
    for route_name, route_info in REST_ROUTE_INFO.items():
        match_param = "member={}".format(resource_name)

        # When action is enabled get info for each action enabled method
        action_info_list = []
        if not route_info.get('disable_actions', False):
            for member in inspect.getmembers(cls, predicate=inspect.ismethod):
                # Get action info from the method definition
                action_info = getattr(member[1], '__action__', None)
                # Check if current action type for current route
                if action_info and action_info.get('type') == route_name:
                    action_info_list.append(action_info)

        # Attach action methods to current route
        for action_info in action_info_list:
            # Init permission for action calls
            permission_name = action_info.get('permission')
            if permission_name:
                permission = permission_name
            else:
                permission = cls.model.get_permission('action')

            # Add a view also for implicit action call
            config.add_view(
                cls,
                attr=action_info['attr_name'],
                match_param=match_param,
                route_name=route_info['route_name'],
                # TODO: Add a decorator to raise method not allowed
                #       instead the default 404 error.
                #decorator=restrict_request_methods,
                request_param=(action_info['name'] + '='),
                renderer='json',
                request_method=action_info['request_method'],
                permission=permission)
            # Add a view also for explicit action call
            config.add_view(
                cls,
                attr=action_info['attr_name'],
                match_param=match_param,
                route_name=route_info['route_name'],
                request_param=("action=" + action_info['name']),
                renderer='json',
                request_method=action_info['request_method'],
                permission=permission)

        # Add views to handle different request methods in this view
        for request_method in route_info['methods']:
            # Init the name of the methos that the class should
            # implement to handle requests for current request method
            attr_name = '{0}_{1}'.format(request_method.lower(), route_name)
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
