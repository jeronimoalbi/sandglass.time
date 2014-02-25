from colander import Integer
from colander import drop
from colander import MappingSchema
from colander import SchemaNode
from colander import SequenceSchema


class BaseModelSchema(MappingSchema):
    """
    Base Schema definition.

    """
    id = SchemaNode(Integer(), missing=drop)


class IdListSchema(SequenceSchema):
    """
    Schema definition for a List of "ids".

    """
    id = SchemaNode(Integer())
