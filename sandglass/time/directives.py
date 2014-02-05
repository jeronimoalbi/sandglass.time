import inspect

from pyramid.path import DottedNameResolver


def is_collection_name(name):
    """
    Check if a name has "_collection" suffix.

    Return a Boolean.

    """
    return name.endswith('_collection')


def is_member_name(name):
    """
    Check if a name has "_member" suffix.

    Return a Boolean.

    """
    return name.endswith('_member')


def is_related_name(name):
    """
    Check if a name has "_related" suffix.

    Return a Boolean.

    """
    return name.endswith('_related')


def add_rest_resource(config, cls_or_dotted):
    """
    Add routes and views for a `RestResource` class.

    """
    # Get the resource class definition
    resolver = DottedNameResolver()
    cls = resolver.maybe_resolve(cls_or_dotted)

    resource_name = cls.get_route_prefix()
    resource_prefix = '/{}/'.format(resource_name)
    resource_data = (
        # /route_prefix/
        #    GET: List all items
        #    POST: Create new item(s)
        #    DELETE: Delete all items
        {'path': resource_prefix,
         'name_suffix': '_collection',
         'methods': ('GET', 'POST', 'DELETE'),
         'enable_rpc': True, },
        # /route_prefix/{pk}/
        #    GET: Get a single item
        #    PUT: Update a single item
        #    DELETE: Delete a single item
        {'path': (resource_prefix + '{pk}/'),
         'name_suffix': '_member',
         'methods': ('GET', 'PUT', 'DELETE', 'POST'),
         'enable_rpc': True, },
        # /route_prefix/{pk}/{related_name}/
        #    GET: List all related items
        #    DELETE: Delete related item(s)
        {'path': (resource_prefix + '{pk}/{related_name}/'),
         'name_suffix': '_related',
         'methods': ('GET', 'DELETE'),
         'enable_rpc': False, },
    )

    # Generate routes and attach views for current class
    for data in resource_data:
        route_name = resource_name + data['name_suffix']
        request_methods = data['methods']
        # Create a new URL route
        config.add_route(route_name,
                         pattern=data['path'],
                         request_method=request_methods)

        # When RPC is enabled get info for each RPC enabled method
        rpc_info_list = []
        if data['enable_rpc']:
            for member in inspect.getmembers(cls, predicate=inspect.ismethod):
                # Get RPC info from the method definition
                rpc_info = getattr(member[1], '__rpc__', None)
                if rpc_info:
                    rpc_info_list.append(rpc_info)

        # Attach RPC methods to current route
        for rpc_info in rpc_info_list:
            # Check if current RPC info describes rules for current resource
            rpc_type = rpc_info.get('type')
            if rpc_type == 'member' and not is_member_name(route_name):
                continue
            if rpc_type == 'collection' and not is_collection_name(route_name):
                continue

            config.add_view(cls,
                            attr=rpc_info['attr_name'],
                            route_name=route_name,
                            # TODO: Add a decorator to raise method not allowed
                            #       instead the default 404 error.
                            #decorator=restrict_request_methods,
                            request_param=(rpc_info['name'] + '='),
                            renderer='json',
                            request_method=rpc_info['request_method'])
            # Add a view also for explicit RPC call
            config.add_view(cls,
                            attr=rpc_info['attr_name'],
                            route_name=route_name,
                            request_param=("action=" + rpc_info['name']),
                            renderer='json',
                            request_method=rpc_info['request_method'])

        # Add views to handle different request methods in this view
        for method in request_methods:
            # Init the name of the methos that the class should
            # implement to handle requests for current request method
            attr_name = '{0}{1}'.format(method.lower(), data['name_suffix'])
            view_handler = getattr(cls, attr_name, None)
            # Skip non callable attributes
            if not hasattr(view_handler, '__call__'):
                continue

            config.add_view(cls,
                            attr=attr_name,
                            route_name=route_name,
                            renderer='json',
                            request_method=method)
