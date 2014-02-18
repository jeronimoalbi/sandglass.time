from sandglass.time.api.model import ModelResource
from sandglass.time.schemas.group import GroupListSchema
from sandglass.time.schemas.group import GroupSchema
from sandglass.time.models.group import Group


class GroupResource(ModelResource):
    """
    REST API resource for Group model.

    """
    name = 'groups'
    model = Group
    schema = GroupSchema
    list_schema = GroupListSchema
