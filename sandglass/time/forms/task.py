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
    name = SchemaNode(String(), validator=Length(min=3))
    short_name = SchemaNode(String(), validator=Length(max=16))
    parent_id = SchemaNode(Integer())
    project_id = SchemaNode(Integer())


class TaskListSchema(SequenceSchema):
    task = TaskSchema()
