from colander import Integer
from colander import Invalid
from colander import drop
from colander import MappingSchema
from colander import null
from colander import SchemaNode
from colander import SequenceSchema

from sandglass.time import _


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


class RequirePermissions(object):
    """
    SchemaNode validator to check user permissions during serialization.

    Validator check that current logged in user has one or more permissions
    for a given schema field.

    """
    invalid_msg = _("No permission to change {field_name} value")

    def __init__(self, *permissions):
        self.permissions = set(permissions)

    def __call__(self, node, value):
        request = node.bindings.get('request')
        if not request:
            raise Exception("Validator is not bound to a request")

        error_message = self.invalid_msg.format(field_name=node.name)
        user = request.authenticated_user
        if user:
            # Admin users are allowed to change any field
            if user.is_admin:
                return

            # Check that user user has right permissions for this field
            if self.permissions.issubset(user.permissions):
                return

        raise Invalid(node, error_message)
