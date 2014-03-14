from sandglass.time.resource import add_api_rest_routes


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
        'group.GroupResource',
        'permission.PermissionResource',
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
