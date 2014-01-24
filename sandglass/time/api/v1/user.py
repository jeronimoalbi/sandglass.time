from sandglass.time.api.model import ModelResource
from sandglass.time.models.user import User


class UserResource(ModelResource):
    """
    REST API resource for User model.

    """
    name = 'users'
    model = User
