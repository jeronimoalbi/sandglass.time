import datetime

from pyramid.exceptions import NotFound

from sandglass.time import _
from sandglass.time.api import collection_action
from sandglass.time.api import member_action
from sandglass.time.api.model import ModelResource
from sandglass.time.api.model import use_schema
from sandglass.time.forms.user import UserListSchema
from sandglass.time.forms.user import UserSigninSchema
from sandglass.time.forms.user import UserSchema
from sandglass.time.models.activity import Activity
from sandglass.time.models.group import Group
from sandglass.time.models.user import User
from sandglass.time.response import error_response
from sandglass.time.security import Administrators
from sandglass.time.security import PUBLIC


class UserResource(ModelResource):
    """
    REST API resource for User model.

    """
    name = 'users'
    model = User
    schema = UserSchema
    list_schema = UserListSchema

    @use_schema(UserSigninSchema)
    @collection_action(methods='POST', permission=PUBLIC)
    def signin(self):
        """
        Signin (login) a user.

        """
        data = self.submitted_member_data
        user = User.query().filter_by(email=data['email']).first()
        if (not user) or not user.is_valid_password(data['password']):
            return error_response(_("Invalid sign in credentials"))

        return user

    @collection_action(methods='POST', permission=PUBLIC)
    def signup(self):
        """
        Create a new user.

        """
        # TODO: Validate user by sending a link to the email
        data = self.submitted_member_data
        if User.query().filter_by(email=data['email']).count():
            msg = _("A user with the same E-Mail already exists")
            return error_response(msg)

        user = User(**data)
        session = User.new_session()
        session.add(user)
        session.flush()

        # TODO: Assing only non admin permissions (or a Users group ?)
        admin_group = Group.query().filter_by(name=Administrators).first()
        user.groups.append(admin_group)

        return user

    @collection_action(methods='GET')
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

    @member_action(method='GET')
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
