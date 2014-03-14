from sandglass.time.models.permission import Permission
from sandglass.time.resource.model import ModelResource
from sandglass.time.schemas.permission import PermissionListSchema
from sandglass.time.schemas.permission import PermissionSchema


class PermissionResource(ModelResource):
    """
    REST API resource for Permission model.

    """
    name = 'permissions'
    model = Permission
    schema = PermissionSchema
    list_schema = PermissionListSchema
