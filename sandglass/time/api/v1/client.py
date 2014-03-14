from sandglass.time.api import API
from sandglass.time.models.client import Client
from sandglass.time.resource.model import ModelResource
from sandglass.time.schemas.client import ClientListSchema
from sandglass.time.schemas.client import ClientSchema


class ClientResource(ModelResource):
    """
    REST API resource for Client model.

    """
    name = 'clients'
    model = Client
    schema = ClientSchema
    list_schema = ClientListSchema


API.register('v1', ClientResource)
