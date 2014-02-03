from pyramid.exceptions import NotFound

from sandglass.time.api import rpc
from sandglass.time.api.model import ModelResource
from sandglass.time.forms.user import UserListSchema
from sandglass.time.forms.user import UserSchema
from sandglass.time.models.user import User


class UserResource(ModelResource):
    """
    REST API resource for User model.

    """
    name = 'users'
    model = User
    schema = UserSchema
    list_schema = UserListSchema

    @rpc(method='get')
    def user_by_credential(self):
        """
        Get a User by email or key.

        Return a User or raise HTTP 404.

        """
        email = self.request.GET.get('email')
        key = self.request.GET.get('key')
        filters = {}
        if email:
            filters['email'] = email
        elif key:
            filters['key'] = key
        else:
            user = None

        if filters:
            user = User.query().filter_by(**filters).first()

        if not user:
            raise NotFound()

        return user
