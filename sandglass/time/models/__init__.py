import weakref

from datetime import datetime
from functools import wraps
from inspect import isclass

from pyramid.security import Allow
from pyramid.security import Authenticated
from sqlalchemy import Column
from sqlalchemy import MetaData
from sqlalchemy import Sequence
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import object_mapper
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import Index
from sqlalchemy.sql.expression import func
from sqlalchemy.types import Boolean
from sqlalchemy.types import DateTime
from sqlalchemy.types import Integer
from zope.sqlalchemy import ZopeTransactionExtension

from sandglass.time.utils import mixedmethod


META = MetaData()

DBSESSION = scoped_session(
    # Integrate transaction manager with SQLAlchemy
    sessionmaker(extension=ZopeTransactionExtension())
)

# Dictionary used to map model class names to class definitions
MODEL_REGISTRY = weakref.WeakValueDictionary()


def initialize_database(engine):
    """
    TODO

    """
    META.bind = engine
    DBSESSION.configure(bind=engine)
    META.create_all(engine)

def execute(sql, **kwargs):
    """Execute an SQL statement in global session context

    SQL parameters are given as keyword arguments.
    Parameter inside SQL statement are given using variable names
    prefixed with a ":" character.

    Example statement:
        SELECT * FROM some_table WHERE id = :id

    """
    result = DBSESSION.execute(sql, kwargs)

    return result


def transactional(func):
    """
    Decorator to add implicit session support to a method.

    Wrapped method will receive an extra argument with a new database session.

    """
    @wraps(func)
    def transactional_wrap(self):
        session = DBSESSION()
        return func(self, session)

    return transactional_wrap


def create_index(cls, *fields, **kwargs):
    """
    Create a new index for the given BaseModel class field(s).

    First field name is used when keywords suffix is not given.
    By default suffix is the first field name.

    Return an Index.

    """
    suffix = kwargs.get('suffix', fields[0])
    table_name = cls.__tablename__
    index_name = 'idx_{0}_{1}'.format(table_name, suffix)
    return Index(index_name, *fields)

def clear_tables():
    """
    Clear all tables, but leave DB structure whole 
    """
    for table in reversed(META.sorted_tables):
        table.delete().execute()


from pyramid.security import ALL_PERMISSIONS
from pyramid.security import Deny
from pyramid.security import Everyone
DEFAULT_ACL = [
    # Users in 'group:admin' group have full access
    (Allow, 'group:admin', ALL_PERMISSIONS),
    # Last rule to deny all if no rule matched before
    (Deny, Everyone, ALL_PERMISSIONS)
]


# Define base model class for declarative definitions
@as_declarative(metadata=META, class_registry=MODEL_REGISTRY)
class BaseModel(object):
    """
    Base class for declarative models definition.

    This is used as a base class during SQLAlchemy base model definition.

    """
    @declared_attr
    def __acl__(cls):
        """
        ACL (Access Control List) with permission rules for current model.

        Rules apply only to Authenticated users.

        ACL follows C.R.U.D. for each rule (Create, Read, Update and Delete).

        Return an ACL (List).

        """
        acl = []
        for permission_name in ('create', 'read', 'update', 'delete'):
            permission = cls.get_permission(permission_name)
            rule = (Allow, Authenticated, permission)
            acl.append(rule)

        acl.extend(DEFAULT_ACL)

        return acl

    @declared_attr
    def __tablename__(cls):
        # Get sandglass application module name where current model is defined
        if not cls.__module__.startswith('sandglass.'):
            raise Exception('Model is not defined inside a sandglass app !')

        return cls.get_namespaced_name()

    @declared_attr
    def id(cls):
        seq_name = cls.__tablename__ + "_id_seq"
        return Column(Integer, Sequence(seq_name), primary_key=True)

    @classmethod
    def get_namespaced_name(cls):
        """
        Get name for current model with app name as prefix.

        Name is lowercase and has the application name where current
        model class is defined as name prefix.

        Return a String.

        """
        parts = cls.__module__.split('.')
        return "{0}_{1}".format(parts[1], cls.__name__.lower())

    @classmethod
    def get_permission(cls, permission_name):
        """
        Get a permission for current model.

        Return a String.

        """
        prefix = cls.get_namespaced_name()
        return "{0}_{1}".format(prefix, permission_name)

    def __iter__(self):
        self._mapper = object_mapper(self)
        self._col_iter = iter(self._mapper.columns)

        return self

    def __str__(self):
        # Call unicode to get value and encode str as UTF8
        return unicode(self).encode('utf8')

    def __json__(self, request):
        data = dict(self)
        return self.update_json_data(data)

    @staticmethod
    def new_session():
        """Create a new Session

        New Sessions must be finished by calling commit()
        or rollback() session methods.

        """
        return DBSESSION()

    @mixedmethod
    def query(obj, session=None):
        """
        Get a query instance for current model class or instance.

        Session argument is used only when method is called as class method.
        Global session is used for class method calls without a session
        argument.

        When query is called on an instance then it will be filtered by
        the instance `id` field.

        """
        if isclass(obj):
            cls = obj
            # For class method calls use global session when none is available
            if not session:
                session = cls.new_session()

            # Create a Query to get all records for current class
            query = session.query(cls)
        else:
            # When called as instance method get class and session from object
            cls = obj.__class__
            session = obj.current_session
            # Create a Query that filters records for current object
            query = session.query(cls).filter(cls.id==obj.id)

        return query

    @classmethod
    def get_attributes_by_name(cls, *field_names):
        """
        Get a list of Model field attributes for the given names.

        If an attribute does not exists it is ignored.

        Return a List.

        """
        columns = cls.__table__.columns
        attr_list = []
        for name in field_names:
            # Skip non column field
            if name not in columns:
                # TODO: Skip non public fields lile user "salt"
                continue

            attr = getattr(cls, name)
            attr_list.append(attr)

        return attr_list

    @classmethod
    def query_from(cls, statement, session=None):
        """
        Get a query instance for current model class using select
        statement to get data.

        """
        query = cls.query(session=session)
        return query.from_statement(statement)

    @classmethod
    def get(cls, *args, **kw):
        """
        Shortcut to get a model instance using SQLAlchemy
        ORM model get method.

        Session can be given as keyword argument.

        """
        session = None
        if 'session' in kw:
            session = kw['session']
            del kw['session']

        query = cls.query(session=session)
        return query.get(*args, **kw)

    @property
    def current_session(self):
        """
        Get current instance Session.

        """
        return DBSESSION.object_session(self)

    def update_json_data(self, obj_dict):
        """
        Method called by __json__ after a dict for current obj is created.

        Override this method to add extra data during JSON serialization.

        Return a Dictionary.

        """
        return obj_dict

    def next(self):
        # Skip non public properties
        column = self._col_iter.next()
        mapper_property = self._mapper.get_property_by_column(column)
        field_name = mapper_property.key

        while field_name.startswith('_'):
            column = self._col_iter.next()
            mapper_property = self._mapper.get_property_by_column(column)
            field_name = mapper_property.key

        field_value = getattr(self, field_name)

        return (field_name, field_value)


class TimestampMixin(object):
    """
    Model MixIn to add created and modified fields.

    """
    created = Column(DateTime, default=func.now())
    modified = Column(DateTime, onupdate=datetime.now)


class ActivePeriodMixin(object):
    """
    Model MixIn to add active flag and period fields.

    """
    is_active = Column(Boolean, default=True)
    active_from = Column(DateTime)
    active_until = Column(DateTime)
