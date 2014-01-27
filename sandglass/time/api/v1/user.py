from sandglass.time.api.model import ModelResource
from sandglass.time.models.user import User
from sandglass.time.forms.user import UserListSchema
from sandglass.time.forms.user import UserSchema


class UserResource(ModelResource):
    """
    REST API resource for User model.

    """
    name = 'users'
    model = User
    schema = UserSchema
    list_schema = UserListSchema

    def before_session_add(self, user):
        user.generate_key()
