from datetime.datetime import now
from sqlalchemy import Column
from sqlalchemy.schema import ForeignKey
from sqlalchemy.types import DateTime
from sqlalchemy.types import Enum
from sqlalchemy.types import Integer
from sqlalchemy.types import UnicodeText

from sandglass.time import _
from sandglass.time.models import BaseModel


# Activity codes
ACTIVITY_UNASSIGNED = 'unassigned'
ACTIVITY_WORKING = 'working'
ACTIVITY_BREAK = 'break'
ACTIVITY_TRIP = 'trip'
INACTIVITY_VACATION = 'vacation'
INACTIVITY_HOLIDAY = 'holiday'
INACTIVITY_SICK = 'sick'
INACTIVITY_ONLEAVE = 'onleave'
INACTIVITY_APPOINTMENT = 'appointment'

# Supported types of tags
ACTIVITY_TYPES = {
    ACTIVITY_UNASSIGNED: _(u"unassigned"),
    ACTIVITY_WORKING: _(u"working"),
    ACTIVITY_BREAK: _(u"on break"),
    ACTIVITY_TRIP: _(u"business trip"),
    INACTIVITY_VACATION: _(u"on vacation"),
    INACTIVITY_HOLIDAY: _(u"public holiday"),
    INACTIVITY_SICK: _(u"sick"),
    INACTIVITY_ONLEAVE: _(u"on leave"),
    INACTIVITY_APPOINTMENT: _(u"official appointment"),
}


class Activity(BaseModel):
    """
    TODO

    """
    description = Column(
        UnicodeText(255), nullable=False)
    start = Column(
        DateTime(timezone=True),
        nullable=False,
        default=now)
    end = Column(
        DateTime(timezone=True))
    activity_type = Column(
        Enum(*ACTIVITY_TYPES.keys(), native_enum=False),
        default=ACTIVITY_UNASSIGNED,
        nullable=False)
    project_id = Column(
        Integer, ForeignKey('project.id'))
    task_id = Column(
        Integer, ForeignKey('task.id'))
