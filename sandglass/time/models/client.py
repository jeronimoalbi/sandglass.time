from sqlalchemy import Column
from sqlalchemy.orm import relationship
from sqlalchemy.types import Unicode

from sandglass.time.models import BaseModel


class Client(BaseModel):
    """
    Model definition for company clients.

    """
    name = Column(Unicode(50), nullable=False)
    projects = relationship("Project", back_populates="client")
