from pyramid.decorator import reify
from pyramid.path import DottedNameResolver

from sandglass.time import _
from sandglass.time.filters import QueryFilter
from sandglass.time.filters import QueryFilterError


class CollectionByPrimaryKey(QueryFilter):
    """
    Filter query results for a list of IDs.

    This filter only works on collections.

    """
    applies_to_admin = True

    # Supported request methods for this filter
    supported_methods = ('GET', )

    def __init__(self, model, *args, **kwargs):
        super(CollectionByPrimaryKey, self).__init__(*args, **kwargs)
        self._model = model

    @reify
    def model(self):
        # When model is not a class resolve it to be a class
        resolver = DottedNameResolver()
        return resolver.maybe_resolve(self._model)

    def applies_to(self, resource):
        if resource.request.method not in self.supported_methods:
            return False
        elif not resource.is_collection_request:
            return False

        return super(CollectionByPrimaryKey, self).applies_to(resource)

    @staticmethod
    def validate(values):
        # Add a limit for the number of values
        max_values = 100
        if len(values) > max_values:
            msg = _(u"A maximum of {} IDs are allowed per request")
            return msg.format(max_values)

        # Check each value in list
        for value in values:
            try:
                int(value)
            except (ValueError, TypeError):
                return _(u"Invalid ID value")

    def filter_query(self, query, request, resource):
        if 'id' not in request.GET:
            return query

        id_list = request.GET.getall('id')
        message = self.validate(id_list)
        if message:
            raise QueryFilterError(message)

        return query.filter(self.model.id.in_(id_list))
