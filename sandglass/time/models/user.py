import hashlib
import os

from sqlalchemy import Column
from sqlalchemy.orm import relationship
from sqlalchemy.types import Unicode
from sqlalchemy.types import UnicodeText

from sandglass.time.models import BaseModel
from sandglass.time.models import TimestampMixin


class User(TimestampMixin, BaseModel):
    """
    TODO

    """
    email = Column(UnicodeText(255), nullable=False, unique=True)
    first_name = Column(UnicodeText(60), nullable=False)
    last_name = Column(UnicodeText(80), nullable=False)
    key = Column(Unicode(64), nullable=False, unique=True)
    salt = Column(Unicode(40), nullable=False)

    tags = relationship("Tag", backref="user")
    projects = relationship("Project", backref="user")
    tasks = relationship("Task", backref="user")

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        # Generate key and salt values the very first time
        # a User is created (this is not called during deserialization)
        if not self.salt:
            self.generate_salt()
        if not self.key:
            self.generate_key()

    @classmethod
    def get_by_email(cls, email):
        """
        Get user by email.

        Return a User or None.

        """
        query = cls.query()
        query = query.filter(cls.email==email)
        return query.first()

    @classmethod
    def get_by_key(cls, key):
        """
        Get user by key.

        Return a User or None.

        """
        query = cls.query()
        query = query.filter(cls.key==key)
        return query.first()

    def generate_salt(self):
        """
        Generate a new random value for salt.

        Return a String with the new value.

        """
        sha_obj = hashlib.sha1(os.urandom(48))
        self.salt = unicode(sha_obj.hexdigest())
        return self.salt

    def generate_key(self):
        """
        Generate a new random user key.

        A new salt value is generated when user has no salt value.

        Return a String with the new key value.

        """
        salt = (self.salt or self.generate_salt())
        sha_obj = hashlib.sha256(os.urandom(48) + salt.encode('utf8'))
        self.key = unicode(sha_obj.hexdigest())
        return self.key
