from colander import drop
from colander import Integer
from colander import Length
from colander import SchemaNode
from colander import String
from colander import SequenceSchema

from sandglass.time.schemas import BaseModelSchema


class TaskSchema(BaseModelSchema):
    """
    Schema definition for Task model.

    """
    name = SchemaNode(
        String(),
        validator=Length(min=3))
    parent_id = SchemaNode(
        Integer(),
        missing=drop)
    project_id = SchemaNode(
        Integer(),
        missing=drop)
    user_id = SchemaNode(
        Integer())


class TaskListSchema(SequenceSchema):
    task = TaskSchema()
