from sandglass.time.api.model import ModelResource
from sandglass.time.models.user import User
from sandglass.time.forms.user import UserSchema
from sandglass.time.forms.user import Users


class UserResource(ModelResource):
    """
    REST API resource for User model.

    """
    name = 'users'
    model = User
    schema = UserSchema
    # list_schema = 'sandglass.time.forms.user.UserListSchema'
    list_schema = Users

    def post_all(self):
        # TODO
        cstruct = self.request.json_body
        deserialized = self.list_schema().deserialize(cstruct)
        print deserialized

        return