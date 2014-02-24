from sqlalchemy import Column
from sqlalchemy.orm import relationship
from sqlalchemy.types import Unicode

from sandglass.time.models import BaseModel


class Client(BaseModel):
    """
    TODO

    """
    name = Column(Unicode(50), nullable=False)
    projects = relationship("Project", backref="client")
