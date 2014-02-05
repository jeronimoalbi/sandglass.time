from colander import drop
from colander import Integer
from colander import Length
from colander import SchemaNode
from colander import String
from colander import SequenceSchema

from sandglass.time.forms import BaseModelSchema


class TaskSchema(BaseModelSchema):
    """
    Schema definition for Task model.

    """
    name = SchemaNode(
        String(),
        validator=Length(min=3))
    short_name = SchemaNode(
        String(),
        missing=drop,
        validator=Length(max=16))
    parent_id = SchemaNode(
        Integer(),
        missing=drop)
    project_id = SchemaNode(
        Integer(),
        missing=drop)


class TaskListSchema(SequenceSchema):
    task = TaskSchema()
