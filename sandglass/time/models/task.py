from sqlalchemy import Column
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship
from sqlalchemy.schema import ForeignKey
from sqlalchemy.types import Integer
from sqlalchemy.types import Unicode
from sqlalchemy.types import UnicodeText

from sandglass.time.models import BaseModel
from sandglass.time.models import create_index


class Task(BaseModel):
    """
    Main activity categorization for projects.

    Describes project phases, parts and areas.

    """
    name = Column(
        UnicodeText(255),
        nullable=False)
    parent_id = Column(
        Integer,
        ForeignKey('time_task.id'))
    project_id = Column(
        Integer,
        ForeignKey('time_project.id'))
    user_id = Column(
        Integer,
        ForeignKey('time_user.id'),
        nullable=False)

    children = relationship(
        "Task",
        lazy=True,
        join_depth=1,
        # Resolve remote side field using an inline callable
        remote_side=(lambda: Task.id),
        backref="parent")

    @declared_attr
    def __table_args__(cls):
        return (
            # Create field indexes
            create_index(cls, 'name'),
        )
