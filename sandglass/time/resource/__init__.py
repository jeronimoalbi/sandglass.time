def includeme(config):
    from .directives import add_api_rest_routes
    from .directives import add_rest_resource

    config.add_directive('add_rest_resource', add_rest_resource)
    config.add_directive('add_api_rest_routes', add_api_rest_routes)
