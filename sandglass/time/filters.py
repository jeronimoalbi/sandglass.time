from pyramid.security import authenticated_userid
from sqlalchemy import or_

# Gobal to avoild "linting" errors defining filter conditions
NULL = None


class QueryFilter(object):
    """
    Base class for ORM Query filtering.

    """
    # When this value is True, apply filter to admin users too.
    # By default no filtering is done for admin users.
    applies_to_admin = False

    def applies_to(self, resource):
        """
        Check if filter applies to a resource.

        Returns a Boolean.

        """
        # TODO: Check that a user is valid
        user = resource.request.authenticated_user
        return user.is_admin and self.applies_to_admin

    def filter_query(self, query, request, resource):
        """
        Method called to filter a query for a request and resource.

        Returns a Query.

        """
        raise NotImplementedError()


class ByCurrentUser(QueryFilter):
    """
    Filter query results for current user.

    By default `user_id` field is used for filtering results
    for current user.

    By default results without user are not filtered.

    """
    user_field_name = 'user_id'

    def __init__(self, filter_nulls=False, *args, **kwargs):
        super(ByCurrentUser, self).__init__(*args, **kwargs)
        self.filter_nulls = filter_nulls

    def filter_query(self, query, request, resource):
        model = resource.model
        field = getattr(model, self.user_field_name)
        filters = field == authenticated_userid(request)
        if not self.filter_nulls:
            filters = or_(filters, field == NULL)

        return query.filter(filters)


class BySearchFields(QueryFilter):
    """
    Filter query results by some search field(s).

    By default filter works only for GET requests.

    Filtering is done only for member model fields, and not for related
    models.
    Filtering using many conditions for the same field is not supported.

    """
    applies_to_admin = True

    # Supported request methods for this filter
    supported_methods = ('GET', )

    # Available filter operations
    filter_operations = (
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

    def __init__(self, model, fields, *args, **kwargs):
        super(BySearchFields, self).__init__(*args, **kwargs)
        self.fields = fields
        self.model = model

    @property
    def fields(self):
        return self._fields

    @fields.setter
    def fields(self, value):
        self._fields = value
        # Change field properties to make filtering work
        for field in value.values():
            # Allow empty values to support NULL filters
            field.missing = None

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
            is_valid_operation = filter_op in self.filter_operations
            if field_name not in self.fields or not is_valid_operation:
                continue

            # Get deserialized field value
            value = self.get_field_value(field_name, value)
            # Apply operation to query
            query = self.apply_operation(query, field_name, filter_op, value)

        return query
