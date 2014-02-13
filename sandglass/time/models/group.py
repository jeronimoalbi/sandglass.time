from sqlalchemy import Column
from sqlalchemy.orm import relationship
from sqlalchemy.schema import ForeignKey
from sqlalchemy.schema import Table
from sqlalchemy.types import Integer
from sqlalchemy.types import Unicode
from sqlalchemy.types import UnicodeText

from sandglass.time.models import BaseModel
from sandglass.time.models import META


# Table definition to relate groups and users
user_association_table = Table(
    'time_group_user',
    META,
    Column('group_id', Integer, ForeignKey('time_group.id')),
    Column('user_id', Integer, ForeignKey('time_user.id')),
)


class Group(BaseModel):
    """
    Model definition for groups of users.

    """
    name = Column(Unicode(50), nullable=False)
    description = Column(UnicodeText(255))

    users = relationship(
        "User",
        secondary=user_association_table,
        backref='groups')

    def __unicode__(self):
        # Use application name as prefix for group name
        return u"time.{}".format(self.name)
