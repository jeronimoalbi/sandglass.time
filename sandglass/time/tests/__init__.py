# pylint: disable=0903

import base64
import inspect
import os
import unittest

from fixture import SQLAlchemyFixture
from fixture import DataSet
from fixture.style import NamedDataStyle
from paste.deploy.loadwsgi import appconfig
from pyramid import testing
from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker
from webtest import TestApp
from zope.sqlalchemy import ZopeTransactionExtension

from sandglass.time import install
from sandglass.time.install import GroupData
from sandglass.time import models
from sandglass.time.models import client
from sandglass.time.models import group
from sandglass.time.models import project
from sandglass.time.models import tag
from sandglass.time.models import task
from sandglass.time.models import user
from sandglass.time.models import activity


def get_static_test_dir():
    """
    Get path to static files directory for tests.

    Static directory contains all non python files needed
    for the tests to be run.

    Return a String with the directory path.

    """
    tests_dir = os.path.dirname(__file__)
    return os.path.join(tests_dir, 'static')


def get_config_file_path():
    """
    Get path to tests config file `sandglass-tests.ini`

    Config file is looked up in current working directory.

    Return a String.

    """
    file_name = 'sandglass-tests.ini'
    cwd_path = os.getcwd()
    file_path = os.path.join(cwd_path, file_name)
    return os.path.join(file_path)


# Load tests settings
SETTINGS = appconfig('config:' + get_config_file_path())

# Create the db-fixtures
FIXTURE = SQLAlchemyFixture(
    env={
        'Group': group.Group,
        'User': user.User,
        'Auth': user.User,
        'Client': client.Client,
        'Project': project.Project,
        'Tag': tag.Tag,
        'Task': task.Task,
        'Activity': activity.Activity,
    },
    style=NamedDataStyle(),
    engine=engine_from_config(SETTINGS, prefix='database.'),
)


def fixture(*datasets):
    """
    Test method decorator that sets up a fixture before test is run.

    """
    def fixture_wrapper(func):
        wrapper = FIXTURE.with_data(*datasets)
        return wrapper(func)

    return fixture_wrapper


class BaseFixture(object):
    """
    Base class with util functions for fixtures.

    """
    @classmethod
    def to_dict(cls):
        """
        Get a dictionary with class attributes.

        Returns a Dictionary.

        """
        data = {}
        for attr_name in dir(cls):
            value = getattr(cls, attr_name)
            is_public = not attr_name.startswith('__')
            is_attribute = not inspect.ismethod(value)
            name_is_valid = attr_name not in ('_dataset', 'ref')
            if is_public and is_attribute and name_is_valid:
                data[attr_name] = value

        return data

# Testuser for Auth
class AuthData(DataSet):

    class testuser(BaseFixture):
        first_name = u"test"
        last_name = u"user"
        email = u"testuser@wienfluss.net"
        password = "1234"
        token = "058bb38b25ddefa3f20537fd8762633dd2c3472f36f9b6628662624fffc7cbc2"
        key = "56f750326fe58c2266e864d4cd95c6ea2877ce9aa5da0b73ef57f2e8774433a4"
        salt = "a66a328e85e9d74da8dac441cb6f5578c530c70f"
        groups = [GroupData.Admins]


class BaseTestCase(unittest.TestCase):
    """
    Base class for all tests.

    """
    @classmethod
    def setUpClass(cls):
        from sandglass.time.models import META

        # Make global database session a non scoped session
        models.DBSESSION = sessionmaker(extension=ZopeTransactionExtension())

        # Initialize some useful class variables
        # to be available in all test classes
        cls.meta = META
        cls.Session = models.DBSESSION
        cls.settings = SETTINGS
        cls.engine = engine_from_config(cls.settings, prefix='database.')

        super(BaseTestCase, cls).setUpClass()

    @classmethod
    def setup_application(cls):
        request = testing.DummyRequest()
        # Initialize Pyramid testing environment support
        cls.config = testing.setUp(settings=cls.settings, request=request)
        cls.config.include('sandglass.time')
        #install.database_insert_default_data()

    @classmethod
    def cleanup_application(cls):
        # Drop all database tables when tests are finished
        cls.meta.drop_all()
        # Cleanup Pyramid testing environment
        testing.tearDown()


class UnitTestCase(BaseTestCase):
    """
    Base class for unit tests.

    Unit tests are small tests that only test 1 thing at a time.

    Database/tables are created at the beginning of each tests and
    tables are dropped after each test finishes.

    """
    def setUp(self):
        self.setup_application()
        super(UnitTestCase, self).setUp()

    def tearDown(self):
        self.cleanup_application()
        super(UnitTestCase, self).tearDown()


class IntegrationTestCase(BaseTestCase):
    """
    Base class for integration tests.

    Database and tables are created before any test is run and
    tables are dropped when all tests are finished.

    """


class FunctionalTestCase(BaseTestCase):
    """
    Base class for functional tests.

    This will integrate with the whole web framework and test
    the full stack of your application.

    Test WSGI application can be accesed as `self.app`.

    Database and tables are created before any test is run and
    tables are dropped when all tests are finished.

    """
    key = None
    token = None
    require_authorization = False

    @classmethod
    def setUpClass(cls):
        super(FunctionalTestCase, cls).setUpClass()
        cls.setup_application()
        cls.wsgi_app = cls.config.make_wsgi_app()

    @classmethod
    def tearDownClass(cls):
        cls.cleanup_application()
        super(FunctionalTestCase, cls).tearDownClass()

    def setUp(self):
        self.app = TestApp(self.wsgi_app)
        # self.init_test_user()

        super(FunctionalTestCase, self).setUp()

    def get_authorization_header(self):
        """
        Get HTTP basic auth headers for current token and key.

        Returns a Dictionary.

        """
        header = {}
        auth_string = "{}:{}".format(AuthData.testuser.token, AuthData.testuser.key)
        auth_string_enc = base64.b64encode(auth_string)
        header['Authorization'] = "Basic {}".format(auth_string_enc)
        return header

    def update_headers(self, headers):
        """
        Update request headers dictionary.

        This is an entry point for tests to override/add/delete
        special HTTP request headers.

        Return a Dictionary.

        """
        if not headers:
            headers = {}

        # Add basig HTTP authorization information
        if self.require_authorization:
            authorization_header = self.get_authorization_header()
            headers.update(authorization_header)

        return headers

    def get_json(self, *args, **kwargs):
        """
        Make a GET request to the application.

        Return a response.

        """
        kwargs['headers'] = self.update_headers(kwargs.get('headers'))
        return self.app.get(*args, **kwargs)

    def post_json(self, *args, **kwargs):
        """
        Make a JSON POST request to the application.

        Return a response.

        """
        kwargs['headers'] = self.update_headers(kwargs.get('headers'))
        return self.app.post_json(*args, **kwargs)

    def put_json(self, *args, **kwargs):
        """
        Make a JSON PUT request to the application.

        Return a response.

        """
        kwargs['headers'] = self.update_headers(kwargs.get('headers'))
        return self.app.put_json(*args, **kwargs)

    def delete_json(self, *args, **kwargs):
        """
        Make a JSON DELETE request to the application.

        Return a response.

        """
        kwargs['headers'] = self.update_headers(kwargs.get('headers'))
        return self.app.delete_json(*args, **kwargs)

    def _create(self, path, content=None, status=200):
        create_response = self.post_json(path, content, status=status)
        created_id = create_response.json[0]['id']
        json = create_response.json

        return (created_id, json)
