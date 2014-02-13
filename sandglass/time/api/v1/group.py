from sandglass.time.api.model import ModelResource
from sandglass.time.forms.group import GroupListSchema
from sandglass.time.forms.group import GroupSchema
from sandglass.time.models.group import Group


class GroupResource(ModelResource):
    """
    REST API resource for Group model.

    """
    name = 'groups'
    model = Group
    schema = GroupSchema
    list_schema = GroupListSchema
