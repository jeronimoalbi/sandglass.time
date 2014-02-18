from colander import drop
from colander import Integer
from colander import Length
from colander import SchemaNode
from colander import String
from colander import SequenceSchema

from sandglass.time.schemas import BaseModelSchema


class TagSchema(BaseModelSchema):
    """
    Schema definition for Tag model.

    """
    name = SchemaNode(
        String(),
        validator=Length(min=3))
    description = SchemaNode(
        String(),
        missing=drop)
    tag_type = SchemaNode(
        String())
    original_id = SchemaNode(
        Integer(),
        missing=drop)
    user_id = SchemaNode(
        Integer())


class TagListSchema(SequenceSchema):
    tag = TagSchema()
