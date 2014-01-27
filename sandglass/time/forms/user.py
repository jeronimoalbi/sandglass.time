from colander import Email
from colander import Length
from colander import SchemaNode
from colander import String
from colander import SequenceSchema

from sandglass.time.forms import BaseModelSchema
from sandglass.time.forms.tag import TagListSchema


class UserSchema(BaseModelSchema):
    """
    Schema definition for user model.

    TODO: define required, missing, default attributes.
    """

    email = SchemaNode(String(), validator=Email())
    first_name = SchemaNode(String(), validator=Length(max=60))
    last_name = SchemaNode(String(), validator=Length(max=80))
    # key = SchemaNode(String(), validator=Length(max=255))
    # salt = SchemaNode(String(), validator=Length(max=255))
    # tags = TagListSchema()


class UserListSchema(SequenceSchema):
    user = UserSchema()


class Users(BaseModelSchema):
    """
    Kind of a proxy schema to access the UserListSchema
    TODO: maybe this can be prevented somehow?
    """
    users = UserListSchema()