from colander import Email
from colander import Length
from colander import SchemaNode
from colander import String
from colander import drop
from colander import SequenceSchema

from sandglass.time.forms import BaseModelSchema


class UserSchema(BaseModelSchema):
    """
    Schema definition for user model.

    """
    email = SchemaNode(
        String(),
        validator=Email())
    first_name = SchemaNode(
        String(),
        validator=Length(max=60))
    last_name = SchemaNode(
        String(),
        validator=Length(max=80))
    password = SchemaNode(
        String(),
        validator=Length(max=30),
        missing=drop)
    data = SchemaNode(
        String(),
        validator=Length(max=255),
        missing=drop)


class UserListSchema(SequenceSchema):
    user = UserSchema()


class UserSignupSchema(UserSchema):
    """
    Schema definition for user signup.

    """
    password = SchemaNode(
        String(),
        validator=Length(max=30))


class UserSigninSchema(BaseModelSchema):
    """
    Schema definition for user logins.

    """
    email = SchemaNode(
        String(),
        validator=Email())
    password = SchemaNode(
        String(),
        validator=Length(max=30))
