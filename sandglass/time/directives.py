from pyramid.path import DottedNameResolver


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
         'name_suffix': '_all',
         'methods': ('GET', 'POST', 'DELETE'),
         'enable_rpc': True, },
        # /route_prefix/{pk}/
        #    GET: Get a single item
        #    PUT: Update a single item
        #    DELETE: Delete a single item
        {'path': (resource_prefix + '{pk}/'),
         'name_suffix': '',
         'methods': ('GET', 'PUT', 'DELETE'),
         'enable_rpc': True, },
        # /route_prefix/{pk}/{related_name}/
        #    GET: List all related items
        #    POST: Create related item(s)
        #    PUT: Update related item(s)
        #    DELETE: Delete related item(s)
        {'path': (resource_prefix + '{pk}/{related_name}/'),
         'name_suffix': '_related',
         'methods': ('GET', 'POST', 'PUT', 'DELETE'),
         'enable_rpc': False, },
    )

    # Name of the entry point method for all RPC calls
    rpc_attr_name = 'handle_rpc_call'
    # Generate routes and attach views for current class
    for data in resource_data:
        route_name = resource_name + data['name_suffix']
        request_methods = data['methods']
        # Create a new URL route
        config.add_route(route_name,
                         pattern=data['path'],
                         request_method=request_methods)
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

        # Attach a view to handle RPC function calls
        rpc_view_handler = getattr(cls, rpc_attr_name, None)
        if data['enable_rpc'] and hasattr(rpc_view_handler, '__call__'):
            config.add_view(cls,
                            attr=rpc_attr_name,
                            route_name=route_name,
                            request_param='call',
                            request_method=('GET', 'POST'))
