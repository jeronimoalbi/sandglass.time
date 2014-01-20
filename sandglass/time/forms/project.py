from colander import Integer
from colander import Length
from colander import SchemaNode
from colander import String

from sandglass.time.forms import BaseModelSchema


class ProjectSchema(BaseModelSchema):
    """
    Schema definition for Project model.

    """
    name = SchemaNode(String(validator=Length(min=3)))
    short_name = SchemaNode(String(validator=Length(max=16)))
    parent_id = SchemaNode(Integer())
    client_id = SchemaNode(Integer())
