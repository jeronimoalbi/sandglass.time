import hashlib
import os

from sqlalchemy import Column
from sqlalchemy.orm import relationship
from sqlalchemy.types import Unicode
from sqlalchemy.types import UnicodeText

from sandglass.time.models import BaseModel
from sandglass.time.models import JSON
from sandglass.time.models import TimestampMixin


class User(TimestampMixin, BaseModel):
    """
    TODO

    """
    token = Column(Unicode(64), nullable=False, unique=True)
    email = Column(UnicodeText(255), nullable=False, unique=True)
    first_name = Column(UnicodeText(60), nullable=False)
    last_name = Column(UnicodeText(80), nullable=False)
    key = Column(Unicode(64), nullable=False)
    salt = Column(Unicode(40), nullable=False)
    # JSON field to support saving extra user data
    data = Column(JSON(255))

    tags = relationship("Tag", backref="user")
    projects = relationship("Project", backref="user")
    tasks = relationship("Task", backref="user")

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        # Generate key and salt values the very first time
        # a User is created (this is not called during deserialization)
        if not self.salt:
            self.generate_salt()

        # Generate a unique user token
        self.token = self.generate_hash()

        if not self.key:
            self.key = self.generate_hash()

    @classmethod
    def get_by_email(cls, email):
        """
        Get user by email.

        Return a User or None.

        """
        query = cls.query()
        query = query.filter(cls.email == email)
        return query.first()

    @classmethod
    def get_by_token(cls, token):
        """
        Get user by token.

        Return a User or None.

        """
        query = cls.query()
        query = query.filter(cls.token == token)
        return query.first()

    def generate_salt(self):
        """
        Generate a new random value for salt.

        Return a String with the new value.

        """
        sha_obj = hashlib.sha1(os.urandom(48))
        self.salt = unicode(sha_obj.hexdigest())
        return self.salt

    def generate_hash(self):
        """
        Generate a new random user hash.

        A new salt value is generated when user has no salt value.

        Return a String with a new hash value.

        """
        salt = (self.salt or self.generate_salt())
        sha_obj = hashlib.sha256(os.urandom(48) + salt.encode('utf8'))
        return unicode(sha_obj.hexdigest())

    def update_json_data(self, data):
        # Add an email hash (can be used for example to get user Gravatar)
        data['email_md5'] = hashlib.md5(self.email).hexdigest()
        return data
