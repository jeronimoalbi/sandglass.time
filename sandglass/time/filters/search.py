from colander import SchemaNode
from zope import interface

from sandglass.time.interfaces import IDescribable
from sandglass.time.filters import NULL
from sandglass.time.filters import QueryFilter
from sandglass.time.filters import QueryFilterError

# List of filter operations
FILTER_OPERATIONS = (
    # Equal / not equal
    'eq',
    'neq',
    # In / not in
    'in',
    'nin',
    # Greater than / equal
    'gt',
    'gte',
    # Lower than / equal
    'lt',
    'lte',
    # Contains (%like%)
    'contains',
    'starts',
    'ends',
    # Is null / not null
    'null',
    'notnull',
)


class Filter(object):
    """
    Base class for search field filter fields.

    """
    def __init__(self, field_type, ops=None):
        self.valid_ops = ops or FILTER_OPERATIONS
        self.node = SchemaNode(field_type, missing=None)

    @property
    def field_type(self):
        return self.node.typ

    def valid_operation(self, operation):
        return operation in self.valid_ops

    def deserialize(self, raw_value):
        return self.node.deserialize(raw_value)


class BySearchFields(QueryFilter):
    """
    Filter query results by some search field(s).

    By default filter works only for GET requests.

    Filtering is done only for member model fields, and not for related
    models.
    Filtering using many conditions for the same field is not supported.

    """
    interface.implements(IDescribable)

    applies_to_admin = True

    # Supported request methods for this filter
    supported_methods = ('GET', )

    # Available filter operations
    filter_operations = FILTER_OPERATIONS

    def __init__(self, model, fields, *args, **kwargs):
        super(BySearchFields, self).__init__(*args, **kwargs)
        self.fields = fields
        self.model = model

    def describe(self):
        fields_info = {}
        for name, field in self.fields.items():
            fields_info[name] = {
                'type': field.field_type.__class__.__name__,
                'operations': field.valid_ops,
            }

        return {
            'name': "search_fields",
            'doc': self.__doc__.strip(),
            'fields': fields_info,
            'methods': self.supported_methods,
        }

    def applies_to(self, resource):
        if resource.request.method not in self.supported_methods:
            return False
        elif not resource.is_collection_request:
            return False

        return super(BySearchFields, self).applies_to(resource)

    def get_field_value(self, field_name, raw_value):
        """
        Get a deserialized value for a field.

        Returns a Python type value.

        """
        if field_name not in self.fields:
            return

        field = self.fields[field_name]
        return field.deserialize(raw_value)

    def apply_operation(self, query, field_name, filter_op, value):
        field_list = self.model.get_attributes_by_name(field_name)
        field = field_list[0]
        if filter_op == 'eq':
            query = query.filter(field == value)
        elif filter_op == 'neq':
            query = query.filter(field != value)
        elif filter_op == 'in' and isinstance(value, list):
            query = query.filter(field.in_(value))
        elif filter_op == 'nin' and isinstance(value, list):
            query = query.filter(~field.in_(value))
        elif filter_op == 'gt':
            query = query.filter(field > value)
        elif filter_op == 'gte':
            query = query.filter(field >= value)
        elif filter_op == 'lt':
            query = query.filter(field < value)
        elif filter_op == 'lte':
            query = query.filter(field <= value)
        elif filter_op == 'contains' and isinstance(value, basestring):
            value = u"%{}%".format(value)
            query = query.filter(field.like(value))
        elif filter_op == 'starts' and isinstance(value, basestring):
            value = u"{}%".format(value)
            query = query.filter(field.like(value))
        elif filter_op == 'ends' and isinstance(value, basestring):
            value = u"%{}".format(value)
            query = query.filter(field.like(value))
        elif filter_op == 'null':
            query = query.filter(field == NULL)
        elif filter_op == 'notnull':
            query = query.filter(field != NULL)

        return query

    def filter_query(self, query, request, resource):
        # Look for filter values in all arguments
        for name, value in request.GET.iteritems():
            # Skip non filter arguments
            if '__' not in name:
                continue

            parts = name.split('__')
            # Skip invalid search filter names
            if len(parts) != 2:
                continue

            # Get field name and operation
            (field_name, filter_op) = parts
            field = self.fields.get(field_name)
            is_valid_operation = filter_op in self.filter_operations
            if is_valid_operation and field:
                # Check that field supports current operation
                is_valid_operation = field.valid_operation(filter_op)

            if not field or not is_valid_operation:
                # Use filter name as error message
                raise QueryFilterError(name)

            # Get deserialized field value
            value = self.get_field_value(field_name, value)
            # Apply operation to query
            query = self.apply_operation(query, field_name, filter_op, value)

        return query
