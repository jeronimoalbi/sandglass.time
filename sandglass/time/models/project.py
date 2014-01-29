from sqlalchemy import Column
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship
from sqlalchemy.schema import ForeignKey
from sqlalchemy.types import Integer
from sqlalchemy.types import Unicode
from sqlalchemy.types import UnicodeText

from sandglass.time.models import BaseModel
from sandglass.time.models import create_index


class Project(BaseModel):
    """
    TODO

    """
    name = Column(UnicodeText(255), nullable=False)
    short_name = Column(Unicode(16))
    client_id = Column(Integer, ForeignKey('time_client.id'))
    parent_id = Column(Integer, ForeignKey('time_project.id'))
    tasks = relationship("Task", backref="project")

    @declared_attr
    def __table_args__(cls):
        return (
            # Create field indexes
            create_index(cls, 'name'),
            create_index(cls, 'short_name'),
        )

    @property
    def is_internal(self):
        """
        Check if project is a company internal projects.

        Return a Boolean.

        """
        return (self.client is None)
