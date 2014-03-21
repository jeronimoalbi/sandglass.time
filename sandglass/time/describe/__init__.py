from __future__ import absolute_import

from .directives import add_resource_describe


def includeme(config):
    config.add_directive('add_resource_describe', add_resource_describe)
