ALL_REQ_METHODS = ('GET', 'POST', 'PUT', 'DELETE')


def add_api_resource(config, cls):
    """
    TODO

    """
    resource_name = cls.get_route_prefix()
    resource_prefix = '/{}/'.format(resource_name)

    # /route_prefix/
    #     GET: list all items
    #     POST: Create new items
    #     DELETE: Delete all items
    config.add_route(resource_name + '_multi',
        pattern=resource_prefix,
        request_method=('GET', 'POST', 'DELETE'))
    config.add_view(cls,
        attr='get_all',
        route_name=(resource_name + '_multi'),
        renderer='json',
        request_method='GET')
    # config.add_view(cls,
    #     attr='post_all',
    #     route_name='',
    #     request_method='POST')
    # config.add_view(cls,
    #     attr='delete_all',
    #     route_name='',
    #     request_method='DELETE')

    # /route_prefix/{pk}/
    #     GET: get single item
    #     PUT: update single item
    #     DELETE: delete single item
    # config.add_route(resource_name + '_single',
    #     pattern=(resource_prefix + '{pk}/'),
    #     request_method=('GET', 'PUT', 'DELETE'))
    # config.add_view(cls,
    #     attr='get',
    #     route_name=(resource_name + '_single'),
    #     request_method='GET')
    # config.add_view(cls,
    #     attr='put',
    #     route_name='',
    #     request_method='PUT')
    # config.add_view(cls,
    #     attr='delete',
    #     route_name='',
    #     request_method='DELETE')
    # config.add_view(cls,
    #     attr='call_method',
    #     route_name='',
    #     request_param='call',
    #     request_method=('GET', 'POST'))

    # /route_prefix/{pk}/{related_name}/
    #     GET: list all related items
    #     POST: create related item(s)
    #     PUT: update related item(s)
    #     DELETE: delete related item(s)
    # config.add_route('',
    #     pattern=(route_prefix + '{pk}/{related_name}/'),
    #     request_method=ALL_REQ_METHODS)
    # config.add_view(cls,
    #     attr='get_all_related',
    #     route_name='',
    #     request_method='GET')
    # config.add_view(cls,
    #     attr='post_all_related',
    #     route_name='',
    #     request_method='POST')
    # config.add_view(cls,
    #     attr='put_all_related',
    #     route_name='',
    #     request_method='PUT')
    # config.add_view(cls,
    #     attr='delete_all_related',
    #     route_name='',
    #     request_method='DELETE')
