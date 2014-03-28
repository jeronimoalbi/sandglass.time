from colander import Boolean
from colander import drop
from colander import Integer
from colander import Length
from colander import SchemaNode
from colander import String
from colander import SequenceSchema

from sandglass.time.schemas import BaseModelSchema
from sandglass.time.schemas import RequirePermissions
from sandglass.time.security import PERMISSION


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
    is_public = SchemaNode(
        Boolean(),
        validator=RequirePermissions(
            PERMISSION.get('project', 'set_is_public', context=__name__)),
        missing=drop)


class ProjectListSchema(SequenceSchema):
    project = ProjectSchema()
