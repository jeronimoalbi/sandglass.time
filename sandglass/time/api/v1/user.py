import datetime

from pyramid.exceptions import NotFound

from sandglass.time import _
from sandglass.time.api import collection_rpc
from sandglass.time.api import member_rpc
from sandglass.time.api.model import ModelResource
from sandglass.time.forms.user import UserListSchema
from sandglass.time.forms.user import UserSchema
from sandglass.time.models.activity import Activity
from sandglass.time.models.user import User
from sandglass.time.response import error_response


class UserResource(ModelResource):
    """
    REST API resource for User model.

    """
    name = 'users'
    model = User
    schema = UserSchema
    list_schema = UserListSchema

    @collection_rpc(methods='GET')
    def search(self):
        """
        Get a User by email or token.

        Return a User or raise HTTP 404.

        """
        user = None
        email = self.request.GET.get('email')
        if email:
            user = User.get_by_email(email)
            if user:
                return user

        token = self.request.GET.get('token')
        if token:
            user = User.get_by_token(token)
            if user:
                return user

        raise NotFound()

    @member_rpc(method='GET')
    def get_activities(self):
        """
        Get activities for current user.

        By default activities are getted only for current day.
        Different date range can be queried using `from` and `to`
        arguments in the request.

        Return a List of Activity.

        """
        if not self.is_valid_object:
            raise NotFound()

        try:
            (from_date, to_date) = self.get_filter_from_to()
        except ValueError, err:
            data = {'message': unicode(err)}
            return error_response(_('Invalid date format'), data=data)

        # When no dates are given use current date as default
        if not from_date and not to_date:
            from_date = datetime.date.today()
            to_date = from_date + datetime.timedelta(days=1)

        query = Activity.query()
        query = query.filter(Activity.user_id == self.pk_value)
        if from_date:
            query = query.filter(Activity.start >= from_date)
        if to_date:
            query = query.filter(Activity.start < to_date)

        return query.all()
