import hashlib

from pyramid.decorator import reify
from sqlalchemy import Column
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship
from sqlalchemy.orm import synonym
from sqlalchemy.orm.util import has_identity
from sqlalchemy.types import Text
from sqlalchemy.types import UnicodeText

from sandglass.time import utils
from sandglass.time.models import BaseModel
from sandglass.time.models import JSON
from sandglass.time.models import TimestampMixin
from sandglass.time.models.group import user_association_table
from sandglass.time.security import Administrators


class User(TimestampMixin, BaseModel):
    """
    Model definition for Sandglass users.

    """
    token = Column(Text(64), nullable=False, unique=True)
    email = Column(UnicodeText(255), nullable=False, unique=True)
    first_name = Column(UnicodeText(60), nullable=False)
    last_name = Column(UnicodeText(80), nullable=False)
    key = Column(Text(64), nullable=False)
    salt = Column(Text(40), nullable=False)
    _password = Column('password', Text(255), nullable=False)
    # JSON field to support saving extra user data
    data = Column(JSON(255))

    tags = relationship(
        "Tag",
        back_populates="user")
    projects = relationship(
        "Project",
        back_populates="user")
    tasks = relationship(
        "Task",
        back_populates="user",
        cascade="all, delete-orphan")
    groups = relationship(
        "Group",
        secondary=user_association_table,
        back_populates="users")

    def __init__(self, *args, **kwargs):
        # Generate user salt during creation
        self.generate_salt()
        super(User, self).__init__(*args, **kwargs)

    def get_password(self):
        return self._password

    def set_password(self, value):
        is_new = has_identity(self)

        # Set password as a hash
        self._password = utils.generate_hash(value, hash='sha1')
        # (Re)generate API token and key after password is updated
        if is_new or not self.token:
            salt = (self.email or '') + self.salt + value
            self.token = utils.generate_random_hash(salt=salt, hash='sha256')
        if is_new or not self.key:
            salt = value + self.salt
            self.key = utils.generate_random_hash(salt=salt, hash='sha256')

    @declared_attr
    def password(cls):
        descriptor = property(cls.get_password, cls.set_password)
        return synonym('_password', descriptor=descriptor)

    @reify
    def is_admin(self):
        """
        Check if user is an administrator.

        Note: Groups will be loaded from database if they are not loaded.

        Returns a Boolean.

        """
        for group in self.groups:
            if group.name == Administrators:
                return True

        return False

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

    def is_valid_password(self, password):
        """
        Check if a plaintext password is valid for current user.

        Return a Boolean.

        """
        return utils.generate_hash(password, hash='sha1') == self.password

    def generate_salt(self):
        """
        Generate a new random value for salt.

        Return a String with the new value.

        """
        self.salt = utils.generate_random_hash(hash='sha1')

    def update_json_data(self, data):
        # Add an email hash (can be used for example to get user Gravatar)
        data['email_md5'] = hashlib.md5(self.email).hexdigest()
        # Remove salt and password from serialized data
        data.pop('salt', None)
        data.pop('password', None)
        return data
