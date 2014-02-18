from sandglass.time.api.model import ModelResource
from sandglass.time.schemas.client import ClientListSchema
from sandglass.time.schemas.client import ClientSchema
from sandglass.time.models.client import Client


class ClientResource(ModelResource):
    """
    REST API resource for Client model.

    """
    name = 'clients'
    model = Client
    schema = ClientSchema
    list_schema = ClientListSchema
