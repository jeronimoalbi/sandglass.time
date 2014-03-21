def includeme(config):
    from .directives import add_resource_describe

    config.add_directive('add_resource_describe', add_resource_describe)
