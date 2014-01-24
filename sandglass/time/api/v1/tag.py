from sandglass.time.api.model import ModelResource
from sandglass.time.models.tag import Tag


class TagResource(ModelResource):
    """
    REST API resource for Tag model.

    """
    name = 'tags'
    model = Tag
