from sqlalchemy import Column
from sqlalchemy.types import Unicode
from sqlalchemy.types import UnicodeText

from sandglass.time.models import BaseModel


class Permission(BaseModel):
    """
    Model definition for permissions.

    """
    name = Column(Unicode(50), nullable=False)
    description = Column(UnicodeText(255))
