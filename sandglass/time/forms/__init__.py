from colander import drop
from colander import Integer
from colander import MappingSchema
from colander import SchemaNode
from colander import SequenceSchema


class BaseModelSchema(MappingSchema):
    """
    Base Schema definition.

    Simple Schema that defines the common "id" field
    that Models define.

    """
    id = SchemaNode(Integer(), missing=drop)


class IDListSchema(SequenceSchema):
    """
    Schema definition for a List of "ids".

    """
    id = SchemaNode(Integer())
