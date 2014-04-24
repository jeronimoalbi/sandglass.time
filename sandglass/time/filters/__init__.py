# Gobal to avoild "linting" errors defining filter conditions
NULL = None


class QueryFilterError(Exception):
    """
    Base exeption for query filters.

    """
    def __init__(self, message):
        self.message = message


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
        user = resource.request.authenticated_user
        if user and user.is_admin:
            return self.applies_to_admin

        # Filter applies to all non admin users by default
        return True

    def filter_query(self, query, request, resource):
        """
        Method called to filter a query for a request and resource.

        Returns a Query.

        """
        raise NotImplementedError()
