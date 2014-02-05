from datetime import datetime
from sqlalchemy import Column
from sqlalchemy.orm import relationship
from sqlalchemy.schema import ForeignKey
from sqlalchemy.schema import Table
from sqlalchemy.types import DateTime
from sqlalchemy.types import Enum
from sqlalchemy.types import Integer
from sqlalchemy.types import UnicodeText

from sandglass.time import _
from sandglass.time.models import BaseModel
from sandglass.time.models import META


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


# Table definition to store the tags used in and activity
tag_association_table = Table(
    'time_activity_tag',
    META,
    Column('activity_id', Integer, ForeignKey('time_activity.id')),
    Column('tag_id', Integer, ForeignKey('time_tag.id')),
)


class Activity(BaseModel):
    """
    A record of activity.

    This is the main unit of measure for sandglass. Activities can describe
    either work on a project, unassigned time, breaks or days where employees
    are away sick or on vacation.

    """
    description = Column(
        UnicodeText(255),
        nullable=False)
    start = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.now)
    end = Column(
        DateTime(timezone=True))
    activity_type = Column(
        Enum(*ACTIVITY_TYPES.keys(), native_enum=False),
        default=ACTIVITY_UNASSIGNED,
        nullable=False)
    project_id = Column(
        Integer,
        ForeignKey('time_project.id'))
    task_id = Column(
        Integer,
        ForeignKey('time_task.id'))
    user_id = Column(
        Integer,
        ForeignKey('time_user.id'),
        nullable=False)

    project = relationship("Project", lazy=True)
    task = relationship("Task", lazy=True)
    user = relationship("User", lazy=True)
    tags = relationship("Tag", secondary=tag_association_table)
