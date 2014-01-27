from sqlalchemy import Column
from sqlalchemy import MetaData
from sqlalchemy import Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import object_mapper
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import Index
from sqlalchemy.types import Integer
from zope.sqlalchemy import ZopeTransactionExtension


META = MetaData()

DBSESSION = scoped_session(
    # Integrate transaction manager with SQLAlchemy
    sessionmaker(extension=ZopeTransactionExtension())
)


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


class DeclarativeBaseModel(object):
    """
    Base class for declarative models definition.

    This is used as a base class during SQLAlchemy base model definition.

    """
    @declared_attr
    def __tablename__(cls):
        # By default table name is the name of model class in lower case
        return cls.__name__.lower()

    @declared_attr
    def id(cls):
        seq_name = cls.__tablename__ + "_id_seq"
        return Column(Integer, Sequence(seq_name), primary_key=True)

    def __iter__(self):
        self._mapper = object_mapper(self)
        self._col_iter = iter(self._mapper.columns)

        return self

    def __repr__(self):
        cls_name = self.__class__.__name__
        description = str(self)

        if description:
            text = '<%s: %s>' % (cls_name, description)
        else:
            text = '<%s>' % cls_name

        return text

    def __str__(self):
        # Call unicode to get value and encode str as UTF8
        return unicode(self).encode('utf8')

    def __json__(self, request):
        return dict(self)

    @staticmethod
    def new_session():
        """Create a new Session

        New Sessions must be finished by calling commit()
        or rollback() session methods.

        """
        return DBSESSION()

    @classmethod
    def query(cls, session=None):
        """
        Get a query instance for current model class.

        """
        # When no session is given use global session
        if not session:
            session = DBSESSION

        query = session.query(cls)
        return query

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


# Define base model class for declarative definitions
BaseModel = declarative_base(name="BaseModel",
                             cls=DeclarativeBaseModel,
                             metadata=META)
