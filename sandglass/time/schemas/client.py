from colander import Length
from colander import SchemaNode
from colander import String
from colander import SequenceSchema

from sandglass.time.schemas import BaseModelSchema


class ClientSchema(BaseModelSchema):
    """
    Schema definition for client model.

    """
    name = SchemaNode(String(), validator=Length(min=3, max=50))


class ClientListSchema(SequenceSchema):
    client = ClientSchema()
