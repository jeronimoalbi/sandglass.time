from sqlalchemy import Column
from sqlalchemy.types import Unicode

from sandglass.time.models import BaseModel


class Client(BaseModel):
    """
    TODO

    """
    name = Column(Unicode(50), nullable=False)
