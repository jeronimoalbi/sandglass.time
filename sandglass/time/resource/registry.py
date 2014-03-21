# Added REST API resources are saved here
RESOURCE_REGISTRY = {}


def register_resource(resource_cls):
    """
    Add a resource class to the global resource registry.

    """
    resource_name = resource_cls.get_route_prefix()
    RESOURCE_REGISTRY[resource_name] = resource_cls
