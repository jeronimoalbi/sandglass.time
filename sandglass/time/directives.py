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

        # When RPC is enabled get info for each RPC enabled method
        rpc_info_list = []
        if not route_info.get('disable_actions', False):
            for member in inspect.getmembers(cls, predicate=inspect.ismethod):
                # Get RPC info from the method definition
                rpc_info = getattr(member[1], '__rpc__', None)
                # Check if current RPC type is the right one for current route
                if rpc_info and rpc_info.get('type') == route_name:
                    rpc_info_list.append(rpc_info)

        # Attach RPC methods to current route
        for rpc_info in rpc_info_list:
            config.add_view(
                cls,
                attr=rpc_info['attr_name'],
                match_param=match_param,
                route_name=route_info['route_name'],
                # TODO: Add a decorator to raise method not allowed
                #       instead the default 404 error.
                #decorator=restrict_request_methods,
                request_param=(rpc_info['name'] + '='),
                renderer='json',
                request_method=rpc_info['request_method'])
            # Add a view also for explicit RPC call
            config.add_view(
                cls,
                attr=rpc_info['attr_name'],
                match_param=match_param,
                route_name=route_info['route_name'],
                request_param=("action=" + rpc_info['name']),
                renderer='json',
                request_method=rpc_info['request_method'])

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
