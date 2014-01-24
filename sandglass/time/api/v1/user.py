from sandglass.time.api import BaseResource


class UserResource(BaseResource):
    """
    REST API resource for User model.

    """
    name = 'users'

    def get_all(self):
        return {}
