from sqlalchemy import Column
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import backref
from sqlalchemy.orm import relationship
from sqlalchemy.schema import ForeignKey
from sqlalchemy.types import Enum
from sqlalchemy.types import Integer
from sqlalchemy.types import Unicode
from sqlalchemy.types import UnicodeText

from sandglass.time.models import BaseModel
from sandglass.time.models import create_index


# Tags used by the system
TAG_TYPE_SYSTEM = u'system'
# Tags used by the accounting users
TAG_TYPE_ACCOUNTING = u'accounting'
# Tags used by employees
TAG_TYPE_ACTIVITY = u'activity'

# Supported types of tags
TAG_TYPES = (TAG_TYPE_SYSTEM, TAG_TYPE_ACCOUNTING, TAG_TYPE_ACTIVITY)


class Tag(BaseModel):
    """
    TODO

    """
    name = Column(UnicodeText(255), nullable=False)
    short_name = Column(Unicode(16))
    description = Column(UnicodeText())
    tag_type = Column(
        Enum(*TAG_TYPES, native_enum=False),
        default=TAG_TYPE_ACTIVITY,
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
            create_index(cls, 'short_name'),
            create_index(cls, 'tag_type'),
        )
