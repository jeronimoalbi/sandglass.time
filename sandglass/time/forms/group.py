from colander import drop
from colander import Length
from colander import SchemaNode
from colander import String
from colander import SequenceSchema

from sandglass.time.forms import BaseModelSchema


class GroupSchema(BaseModelSchema):
    """
    Schema definition for group model.

    """
    # TODO: Validate that name does not contain spaces
    name = SchemaNode(
        String(),
        validator=Length(min=3, max=50))
    description = SchemaNode(
        String(),
        missing=drop)


class GroupListSchema(SequenceSchema):
    client = GroupSchema()
