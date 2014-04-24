try:
    from enum import Enum
except ImportError:
    # Use fallback package for python < 3.4
    from flufl.enum import Enum

from sqlalchemy import Column
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import backref
from sqlalchemy.orm import relationship
from sqlalchemy.schema import ForeignKey
from sqlalchemy.types import Enum as DbEnum
from sqlalchemy.types import Integer
from sqlalchemy.types import UnicodeText

from sandglass.time.models import BaseModel
from sandglass.time.models import create_index


class TAG(Enum):
    # Tags used by the system
    system = u'system'
    # Tags used by the accounting users
    accounting = u'accounting'
    # Tags used by employees
    activity = u'activity'

# Supported types of tags
TAG_TYPES = [item.value for item in TAG]


class Tag(BaseModel):
    """
    Model definition for tags.

    """
    name = Column(
        UnicodeText(40),
        nullable=False)
    description = Column(
        UnicodeText())
    tag_type = Column(
        DbEnum(*TAG_TYPES, native_enum=False),
        default=TAG.activity.value,
        nullable=False)
    original_id = Column(
        Integer,
        ForeignKey('time_tag.id'),
        doc="If current tag is an alias this is the ID of the original tag")
    user_id = Column(
        Integer,
        ForeignKey('time_user.id'),
        nullable=False,
        doc="User that created the tag")

    user = relationship(
        "User",
        uselist=False,
        back_populates="tags")
    aliases = relationship(
        "Tag",
        lazy=True,
        join_depth=1,
        backref=backref("original", remote_side=(lambda: Tag.id)))

    @declared_attr
    def __table_args__(cls):
        return (
            # Create field indexes
            create_index(cls, 'name'),
            create_index(cls, 'tag_type'),
        )
