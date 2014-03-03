from sqlalchemy import Column
from sqlalchemy.orm import relationship
from sqlalchemy.types import Text
from sqlalchemy.types import UnicodeText

from sandglass.time.models import BaseModel
from sandglass.time.models.group import permission_association_table


class Permission(BaseModel):
    """
    Model definition for permissions.

    """
    name = Column(Text(50), nullable=False)
    description = Column(UnicodeText(255))

    groups = relationship(
        "Group",
        secondary=permission_association_table,
        back_populates="permissions")
