from sandglass.time.api.model import ModelResource
from sandglass.time.models.client import Client


class ClientResource(ModelResource):
    """
    REST API resource for Client model.

    """
    name = 'clients'
    model = Client
