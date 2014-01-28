from sandglass.time.api.model import ModelResource
from sandglass.time.models.activity import Activity
from sandglass.time.forms.activity import ActivityListSchema
from sandglass.time.forms.activity import ActivitySchema


class ActivityResource(ModelResource):
    """
    REST API resource for Activity model.

    """
    name = 'activities'
    model = Activity
    schema = ActivitySchema
    list_schema = ActivityListSchema
