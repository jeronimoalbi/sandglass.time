from sqlalchemy import Column
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import backref
from sqlalchemy.orm import relationship
from sqlalchemy.schema import ForeignKey
from sqlalchemy.types import Boolean
from sqlalchemy.types import Integer
from sqlalchemy.types import UnicodeText

from sandglass.time.models import ActivePeriodMixin
from sandglass.time.models import BaseModel
from sandglass.time.models import create_index
from sandglass.time.models.group import project_association_table


class Project(ActivePeriodMixin, BaseModel):
    """
    Project for a ceratain client or internal (for the company itsself).

    Defines a list of tasks (project parts) available to book hours to.

    Projects can be cloned to easily create new projects with the same
    attributes.

    """
    name = Column(
        UnicodeText(255),
        nullable=False)
    client_id = Column(
        Integer,
        ForeignKey('time_client.id'))
    parent_id = Column(
        Integer,
        ForeignKey('time_project.id'))
    user_id = Column(
        Integer,
        ForeignKey('time_user.id'),
        nullable=False)
    is_public = Column(
        Boolean,
        default=False)

    user = relationship(
        "User",
        back_populates="projects")
    client = relationship(
        "Client",
        back_populates="projects")
    tasks = relationship(
        "Task",
        back_populates="project")
    children = relationship(
        "Project",
        lazy=True,
        join_depth=1,
        # Resolve remote side field using an inline callable
        backref=backref("parent", remote_side=(lambda: Project.id)))
    groups = relationship(
        "Group",
        secondary=project_association_table,
        back_populates="projects")

    @declared_attr
    def __table_args__(cls):
        return (
            # Create field indexes
            create_index(cls, 'name'),
        )

    @property
    def is_internal(self):
        """
        Check if project is a company internal projects.

        Return a Boolean.

        """
        return self.client is None
