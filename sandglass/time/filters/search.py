import logging

from colander import SchemaNode
from zope import interface

from sandglass.time import _
from sandglass.time.describe.interfaces import IDescribable
from sandglass.time.filters import NULL
from sandglass.time.filters import QueryFilter
from sandglass.time.filters import QueryFilterError

LOG = logging.getLogger(__name__)

# Global error/warning messages
LOG_MESSAGES = {
    'value_is_not_string': _("Filter value %s is not a string"),
    'value_is_not_list': _("Filter value %s is not a list"),
}


def _apply_operation_eq(query, field, value):
    """
    Apply "is equal" operation to a query field.

    """
    return query.filter(field == value)


def _apply_operation_neq(query, field, value):
    """
    Apply "is not equal" operation to a query field.

    """
    return query.filter(field != value)


def _apply_operation_in(query, field, value):
    """
    Apply "value(s) in list" operation to a query field.

    """
    if isinstance(value, list):
        return query.filter(field.in_(value))
    else:
        LOG.warning(LOG_MESSAGES['value_is_not_list'], value)
        return query


def _apply_operation_nin(query, field, value):
    """
    Apply "value(s) not in list" operation to a query field.

    """
    if isinstance(value, list):
        return query.filter(~field.in_(value))
    else:
        LOG.warning(LOG_MESSAGES['value_is_not_list'], value)
        return query


def _apply_operation_gt(query, field, value):
    """
    Apply "greater than" operation to a query field.

    """
    return query.filter(field > value)


def _apply_operation_gte(query, field, value):
    """
    Apply "greater than or equal" operation to a query field.

    """
    return query.filter(field >= value)


def _apply_operation_lt(query, field, value):
    """
    Apply "lower than" operation to a query field.

    """
    return query.filter(field < value)


def _apply_operation_lte(query, field, value):
    """
    Apply "lower than or equal" operation to a query field.

    """
    return query.filter(field <= value)


def _apply_operation_contains(query, field, value):
    """
    Apply "string contains" operation to a query field.

    """
    if isinstance(value, basestring):
        value = u"%{}%".format(value)
        query = query.filter(field.like(value))
    else:
        LOG.warning(LOG_MESSAGES['value_is_not_string'], value)
        return query


def _apply_operation_starts(query, field, value):
    """
    Apply "string starts with" operation to a query field.

    """
    if isinstance(value, basestring):
        value = u"{}%".format(value)
        query = query.filter(field.like(value))
    else:
        LOG.warning(LOG_MESSAGES['value_is_not_string'], value)
        return query


def _apply_operation_ends(query, field, value):
    """
    Apply "string ends with" operation to a query field.

    """
    if isinstance(value, basestring):
        value = u"%{}".format(value)
        query = query.filter(field.like(value))
    else:
        LOG.warning(LOG_MESSAGES['value_is_not_string'], value)
        return query


def _apply_operation_null(query, field, value):
    """
    Apply "is null" operation to a query field.

    """
    return query.filter(field == NULL)


def _apply_operation_notnull(query, field, value):
    """
    Apply "is not null" operation to a query field.

    """
    return query.filter(field != NULL)


# Query filter operations
FILTER_OPERATIONS = {
    # Equal / not equal
    'eq': _apply_operation_eq,
    'neq': _apply_operation_neq,
    # In / not in
    'in': _apply_operation_in,
    'nin': _apply_operation_nin,
    # Greater than / equal
    'gt': _apply_operation_gt,
    'gte': _apply_operation_gte,
    # Lower than / equal
    'lt': _apply_operation_lt,
    'lte': _apply_operation_lte,
    # Contains (%like%)
    'contains': _apply_operation_contains,
    'starts': _apply_operation_starts,
    'ends': _apply_operation_ends,
    # Is null / not null
    'null': _apply_operation_null,
    'notnull': _apply_operation_notnull,
}


class Filter(object):
    """
    Base class for search field filter fields.

    """
    interface.implements(IDescribable)

    def __init__(self, field_type, ops=None):
        self.valid_ops = ops or FILTER_OPERATIONS.keys()
        self.node = SchemaNode(field_type, missing=None)

    @property
    def field_type(self):
        return self.node.typ

    def valid_operation(self, operation):
        return operation in self.valid_ops

    def deserialize(self, raw_value):
        return self.node.deserialize(raw_value)

    def describe(self):
        type_cls = self.field_type.__class__
        operation_list = []
        for operation in self.valid_ops:
            info = {
                'name': operation,
                'doc': FILTER_OPERATIONS[operation].__doc__,
            }
            operation_list.append(info)

        return {
            'type': type_cls.__name__,
            'operations': operation_list,
        }


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
            fields_info[name] = field.describe()

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
        # When filter operation is not supported return query without filter
        if filter_op not in self.filter_operations:
            return query

        field_list = self.model.get_attributes_by_name(field_name)
        field = field_list[0]
        apply_filter_func = self.filter_operations[filter_op]
        return apply_filter_func(query, field, value)

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
