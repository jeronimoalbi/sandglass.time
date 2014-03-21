def add_resource_describe(config, version, resource):
    """
    Add support to describe API resources.

    Describe can be called as `/@describe` in the API root URL.

    """
    route_name = 'api.{}.describe'.format(version)
    config.add_route(
        route_name,
        '/@describe',
        request_method='GET',
        factory=resource,
    )
    config.add_view(
        resource,
        route_name=route_name,
        renderer='json',
        permission="time.api.describe",
    )
