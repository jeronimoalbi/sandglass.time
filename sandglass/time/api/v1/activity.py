from sandglass.time.api.model import ModelResource
from sandglass.time.models.activity import Activity


class ActivityResource(ModelResource):
    """
    REST API resource for Activity model.

    """
    name = 'activities'
    model = Activity
