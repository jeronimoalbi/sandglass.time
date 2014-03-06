from colander import Integer
from colander import Invalid
from colander import drop
from colander import MappingSchema
from colander import null
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


class Dictionary(object):
    """
    Schema type for Python dictionary fields.

    """
    def serialize(self, node, appstruct):
        if appstruct is null or appstruct is None:
            return null

        if not isinstance(appstruct, dict):
            raise Invalid(node, '%r is not a dictionary' % appstruct)

        # Return given dictionary (don't serialize)
        return appstruct

    def deserialize(self, node, cstruct):
        if cstruct is null or cstruct is None:
            return null

        if not isinstance(cstruct, dict):
            raise Invalid(node, '%r is not a dictionary' % cstruct)

        # Return given dictionary (don't deserialize)
        return cstruct

    def cstruct_children(self, node, cstruct):
        return []
