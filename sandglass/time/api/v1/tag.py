from sandglass.time.api.model import ModelResource
from sandglass.time.forms.tag import TagListSchema
from sandglass.time.forms.tag import TagSchema
from sandglass.time.models.tag import Tag


class TagResource(ModelResource):
    """
    REST API resource for Tag model.

    """
    name = 'tags'
    model = Tag
    schema = TagSchema
    list_schema = TagListSchema
