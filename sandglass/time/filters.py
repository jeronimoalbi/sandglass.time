from pyramid.security import authenticated_userid
from sqlalchemy import or_


class QueryFilter(object):
    """
    Base class for ORM Query filtering.

    """
    # When this value is True, apply filter to admin users too.
    # By default no filtering is done for admin users.
    applies_to_admin = False

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

    def __init__(self, filter_nulls=False):
        self.filter_nulls = filter_nulls

    def filter_query(self, query, request, resource):
        model = resource.model
        field = getattr(model, self.user_field_name)
        filters = field == authenticated_userid(request)
        if not self.filter_nulls:
            filters = or_(filters, field == None)

        return query.filter(filters)
