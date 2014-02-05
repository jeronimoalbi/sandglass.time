from pyramid.exceptions import NotFound

from sandglass.time.api import collection_rpc
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

    @collection_rpc(methods='GET')
    def search(self):
        """
        Get a User by email or key.

        Return a User or raise HTTP 404.

        """
        user = None
        email = self.request.GET.get('email')
        if email:
            user = User.get_by_email(email)
            if user:
                return user

        key = self.request.GET.get('key')
        if key:
            user = User.get_by_key(key)
            if user:
                return user

        raise NotFound()
