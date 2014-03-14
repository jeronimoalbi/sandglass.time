from sandglass.time.api import API
from sandglass.time.models.tag import Tag
from sandglass.time.resource.model import ModelResource
from sandglass.time.schemas.tag import TagListSchema
from sandglass.time.schemas.tag import TagSchema


class TagResource(ModelResource):
    """
    REST API resource for Tag model.

    """
    name = 'tags'
    model = Tag
    schema = TagSchema
    list_schema = TagListSchema


API.register('v1', TagResource)
