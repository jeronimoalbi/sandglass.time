from sandglass.time.api import member_action
from sandglass.time.api.model import ModelResource
from sandglass.time.models.activity import Activity
from sandglass.time.models.tag import Tag
from sandglass.time.schemas import IdListSchema
from sandglass.time.schemas.activity import ActivityListSchema
from sandglass.time.schemas.activity import ActivitySchema


class ActivityResource(ModelResource):
    """
    REST API resource for Activity model.

    """
    name = 'activities'
    model = Activity
    schema = ActivitySchema
    list_schema = ActivityListSchema

    @member_action(methods='POST')
    def add_tags(self):
        """
        Add tags to current activity.

        Return a List of Tags that were added.

        """
        activity = self.object
        id_list_schema = IdListSchema()
        tag_id_list = id_list_schema.deserialize(self.request_data)
        # Get Tag objects for the given IDs
        session = activity.current_session
        query = Tag.query(session=session)
        query = query.filter(Tag.id.in_(tag_id_list))
        tag_list = query.all()
        for tag in tag_list:
            # TODO: Implement it using plain inserts
            activity.tags.append(tag)

        return tag_list

    @member_action(methods='DELETE')
    def remove_tags(self):
        """
        Remove tags from current activity.

        JSON body is a list of integer values with
        Tag IDs to remove.

        """
        activity = self.object
        id_list_schema = IdListSchema()
        tag_id_list = id_list_schema.deserialize(self.request_data)
        removed_tag_list = []
        for tag in activity.tags:
            if tag.id not in tag_id_list:
                continue

            # TODO: Implement it using plain deletes
            activity.tags.remove(tag)
            removed_tag_list.append(tag)

        return removed_tag_list
