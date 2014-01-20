from colander import Length
from colander import SchemaNode
from colander import String

from sandglass.time.forms import BaseModelSchema


class TagSchema(BaseModelSchema):
    """
    Schema definition for Tag model.

    """
    name = SchemaNode(String(validator=Length(min=3)))
    short_name = SchemaNode(String(validator=Length(max=16)))
    description = SchemaNode(String())
    tag_type = SchemaNode(String())
