from colander import drop
from colander import Integer
from colander import Length
from colander import SchemaNode
from colander import String
from colander import SequenceSchema

from sandglass.time.forms import BaseModelSchema


class ProjectSchema(BaseModelSchema):
    """
    Schema definition for Project model.

    """
    name = SchemaNode(
        String(),
        validator=Length(min=3))
    parent_id = SchemaNode(
        Integer(),
        missing=drop)
    client_id = SchemaNode(
        Integer(),
        missing=drop)
    user_id = SchemaNode(
        Integer())


class ProjectListSchema(SequenceSchema):
    project = ProjectSchema()
