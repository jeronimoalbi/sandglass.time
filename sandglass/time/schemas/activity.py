from colander import DateTime
from colander import drop
from colander import Integer
from colander import OneOf
from colander import SchemaNode
from colander import String
from colander import SequenceSchema

from sandglass.time.schemas import BaseModelSchema
from sandglass.time.models.activity import ACTIVITY_TYPES
from sandglass.time.models.activity import ACTIVITY_UNASSIGNED


class ActivitySchema(BaseModelSchema):
    """
    Schema definition for activity model.

    """
    description = SchemaNode(
        String())
    start = SchemaNode(
        DateTime(),
        missing=drop)
    end = SchemaNode(
        DateTime(),
        missing=drop)
    activity_type = SchemaNode(
        String(),
        missing=drop,
        validator=OneOf(ACTIVITY_TYPES.keys()),
        default=ACTIVITY_UNASSIGNED)
    project_id = SchemaNode(
        Integer(),
        missing=drop)
    task_id = SchemaNode(
        Integer(),
        missing=drop)
    user_id = SchemaNode(
        Integer())


class ActivityListSchema(SequenceSchema):
    """
    Schema definition for a list of activities.
    """
    activity = ActivitySchema()
