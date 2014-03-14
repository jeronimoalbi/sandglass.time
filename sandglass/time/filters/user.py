from pyramid.security import authenticated_userid
from sqlalchemy import or_

from sandglass.time.filters import NULL
from sandglass.time.filters import QueryFilter


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
