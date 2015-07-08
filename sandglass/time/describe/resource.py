from zope import interface

from .interfaces import IDescribable


class ResourceDescriber(object):
    """
    API resource describer.

    Base class to describe `BaseResource` instances.

    """
    interface.implements(IDescribable)

    def __init__(self, resource):
        self.resource = resource

    def __json__(self, request):
        return self.describe()

    def describe_actions(self, data):
        filtered_fields = ('type', 'attr_name', 'extra')
        resource = self.resource
        data['actions'] = {'member': [], 'collection': []}
        for name in ('member', 'collection'):
            for action_info in resource.get_actions_by_type(name):
                info = action_info.copy()
                # Add action docstring when available
                func = getattr(resource, info['attr_name'])
                info['doc'] = (func.__doc__ or '').strip()

                # Remove fields that should not be visible
                for filtered_name in filtered_fields:
                    del info[filtered_name]

                data['actions'][name].append(info)

        return data

    def describe(self):
        data = {}
        self.describe_actions(data)
        return data


class ModelResourceDescriber(ResourceDescriber):
    """
    API resource describer for `ModelResource` instances.

    """
    def describe_related(self, data):
        data['related'] = self.resource.relationships.keys()
        return data

    def describe_schema(self, data, schema_cls):
        schema = schema_cls()
        data['schema'] = {}
        for child in schema.children:
            class_name = child.typ.__class__.__name__
            data['schema'][child.name] = {
                'type': class_name,
                'doc': child.description,
            }
        return data

    def describe_action_schemas(self, data):
        if 'actions' not in data:
            return data

        resource = self.resource
        for name in ('member', 'collection'):
            # Save list of schema actions by name
            actions = {info['name']: info for info in data['actions'][name]}
            # Get action schemas for current resource actions
            for action_info in resource.get_actions_by_type(name):
                action_name = action_info['name']
                if action_name not in actions:
                    continue

                func = getattr(resource, action_info['attr_name'])
                schema_cls = getattr(func, '__schema__', None)
                if not schema_cls:
                    continue

                self.describe_schema(actions[action_name], schema_cls)

        return data

    def describe_filters(self, data):
        filters_data = []
        query_filters = self.resource.get_query_filters()
        for filter in query_filters:
            if IDescribable.providedBy(filter):
                filters_data.append(filter.describe())

        if filters_data:
            data['filters'] = filters_data

        return data

    def describe(self):
        data = super(ModelResourceDescriber, self).describe()
        self.describe_schema(data, self.resource.schema)
        self.describe_action_schemas(data)
        self.describe_related(data)
        self.describe_filters(data)
        return data
