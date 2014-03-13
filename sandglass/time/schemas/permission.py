from colander import drop
from colander import Length
from colander import SchemaNode
from colander import String
from colander import SequenceSchema

from sandglass.time.schemas import BaseModelSchema


class PermissionSchema(BaseModelSchema):
    """
    Schema definition for permission model.

    """
    name = SchemaNode(
        String(),
        validator=Length(min=3, max=50))
    description = SchemaNode(
        String(),
        missing=drop)


class PermissionListSchema(SequenceSchema):
    permission = PermissionSchema()
