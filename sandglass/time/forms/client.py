from colander import Length
from colander import SchemaNode
from colander import String

from sandglass.time.forms import BaseModelSchema


class ClientSchema(BaseModelSchema):
    """
    Schema definition for client model.

    """
    name = SchemaNode(String(validator=Length(min=3, max=50)))
