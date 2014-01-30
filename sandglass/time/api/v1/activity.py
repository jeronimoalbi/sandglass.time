from sandglass.time.api import rpc
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

    @rpc(method='post')
    def add_tags(self):
        """
        Add tags to current activity.

        """

    @rpc(method='post')
    def remove_tags(self):
        """
        Remove tags from current activity.

        JSON body is a list of integer values with
        Tag IDs to remove.

        """
        activity = self.object
        # TODO: Create a schema to validate JSON body (has to be a list of ID)
        tag_id_list = self.request.json_body
        # TODO: Return a proper response object
        try:
            return activity.remove_tags(tag_id_list)
        finally:
            activity.current_session.flush()
