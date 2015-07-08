import inspect
import logging

import dateutil.parser

from pyramid.decorator import reify
from zope import interface

from sandglass.time.describe.interfaces import IDescribable
from sandglass.time.describe.resource import ResourceDescriber
from sandglass.time.security import PERMISSION
from sandglass.time.utils import route_path

from .action import collection_action
from .directives import REST_ROUTE_INFO

LOG = logging.getLogger(__name__)


class APIRequestDataError(Exception):
    """
    Exception for invalid API requests.

    API requests uses JSON format to transfer data. This exception
    is raised when data has an invalid format and fails during
    JSON serialization.

    """


class BaseResource(object):
    """
    Base class for Sandglass time API resources.

    """
    interface.implements(IDescribable)

    # Name used as prefix for this resource URLs
    # NOTE: For REST APIs it is recommended to be in plural form
    name = None

    # Class used for describing a API resources
    describer_cls = ResourceDescriber

    @classmethod
    def get_route_prefix(cls):
        """
        Get prefix to be used for current resource URL path.

        Returns a String.

        """
        if not cls.name:
            raise Exception("Resource name can't be empty")

        return cls.name.lower()

    @classmethod
    def get_collection_path(cls):
        """
        Get collection URL path.

        Return a String.

        """
        route_info = REST_ROUTE_INFO['collection']
        route_name = route_info['route_name']
        member = cls.get_route_prefix()
        return route_path(route_name, member=member)

    @classmethod
    def get_member_path(cls, pk):
        """
        Get member URL path.

        Argument `pk` is the primary key value for the member object.

        Return a String.

        """
        route_info = REST_ROUTE_INFO['member']
        route_name = route_info['route_name']
        member = cls.get_route_prefix()
        return route_path(route_name, member=member, pk=pk)

    @classmethod
    def get_related_path(cls, pk, related_name):
        """
        Get member URL path.

        Argument `pk` is the primary key value for the member object,
        and `related_name` is the name of the related object(s).

        Return a String.

        """
        route_info = REST_ROUTE_INFO['related']
        route_name = route_info['route_name']
        member = cls.get_route_prefix()
        return route_path(
            route_name,
            member=member,
            pk=pk,
            related_name=related_name,
        )

    @classmethod
    def get_actions_by_type(cls, action_type):
        """
        Get the list of action information for current class.

        Action type can be member, collection or * for any type.

        Return a List of dictionaries.

        """
        action_info_list = []
        member_list = inspect.getmembers(cls, predicate=inspect.ismethod)
        for member in member_list:
            # Get action info from the method definition
            action_info = getattr(member[1], '__action__', None)
            if not action_info:
                continue

            # Check if current action info match action type
            if action_type != '*':
                if action_info.get('type') != action_type:
                    # Skip current action info when type is not right
                    continue

            action_info_list.append(action_info)

        return action_info_list

    def __init__(self, request):
        self.request = request

    def _get_pk_value(self):
        value = self.request.matchdict.get('pk')
        try:
            pk_value = int(value)
        except (ValueError, TypeError):
            pk_value = None

        return pk_value

    def _get_related_name(self):
        return self.request.matchdict.get('related_name')

    @property
    def is_member_request(self):
        """
        Check if current request is a member request.

        Method checks if pk_value is not None. When no pk value is
        available it means the current is a collection request.

        Return a Boolean.

        """
        return self.pk_value is not None

    @property
    def is_collection_request(self):
        """
        Check if current request is a collection request.

        Method checks if pk_value is None. When no pk value is
        available it means the current is a collection request.

        Return a Boolean.

        """
        return not self.is_member_request

    @property
    def is_related_request(self):
        """
        Check if current request is a related request.

        Method checks if pk_value is not None. When no pk value is
        available it means the current is a collection request.
        It also checks that related_name is available.

        Return a Boolean.

        """
        return self.is_member_request and self.related_name

    @reify
    def request_data(self):
        """
        Get JSON data from current request body.

        Returns a python representation of the JSON.

        """
        try:
            return self.request.json_body
        except ValueError:
            # Exception is also raised when "Content Type"
            # is not "application/json".
            LOG.exception('Invalid JSON in request body')
            raise APIRequestDataError()

    @reify
    def pk_value(self):
        """
        Get primary key value for current request.

        Return an Integer or None.

        """
        return self._get_pk_value()

    @reify
    def related_name(self):
        """
        Get related name when it is available in the URL.

        When no related name is given or the name is not a model
        relationship `NotFound` is raised.

        Return a String.

        """
        return self._get_related_name()

    def get_filter_from_to(self):
        """
        Get from/to request arguments as python dates.

        ValueError is raised when date format is invalid for one
        or both dates.

        Return a Tuple.

        """
        from_date = self.request.params.get('from')
        if from_date:
            # Convert string to date
            from_date = dateutil.parser.parse(from_date)

        to_date = self.request.params.get('to')
        if to_date:
            # Convert string to date
            to_date = dateutil.parser.parse(to_date)

        return (from_date, to_date)

    @collection_action(
        methods='GET',
        permission=PERMISSION.get('api', 'describe'),
    )
    def describe(self):
        """
        Get an API resource description.

        """
        describer = self.describer_cls(self)
        return describer
