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
