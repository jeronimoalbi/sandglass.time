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


class SpaceSeparatedIntegers(object):
    """
    Schema type for space separated list of integer values.

    """
    def serialize(self, node, appstruct):
        if appstruct is null or appstruct is None:
            return null

        if not isinstance(appstruct, list):
            raise Invalid(node, '%r is not a list' % appstruct)

        cstruct = [str(value) for value in appstruct]
        return ' '.join(cstruct)

    def deserialize(self, node, cstruct):
        if cstruct is null or cstruct is None:
            return null

        if not isinstance(cstruct, basestring):
            raise Invalid(node, '%r is not a string' % cstruct)

        try:
            appstruct = [int(value) for value in cstruct.split(' ')]
        except ValueError:
            raise Invalid(node, '%r has invalid integer values' % cstruct)

        return appstruct

    def cstruct_children(self, node, cstruct):
        return []
