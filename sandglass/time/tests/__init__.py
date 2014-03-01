import os

# Set TESTING environmental variable as soon as test is imported
os.environ['TESTING'] = 'true'

import base64
import inspect
import logging
import unittest
import warnings

from functools import wraps

from fixture import SQLAlchemyFixture
from fixture import DataSet
from fixture.style import NamedDataStyle
from paste.deploy.loadwsgi import appconfig
from pyramid import testing
from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker
from webtest import lint
from webtest import TestApp
from zope.sqlalchemy import ZopeTransactionExtension

from sandglass.time import models
from sandglass.time.models import MODEL_REGISTRY
from sandglass.time.install import GroupData


# Filter WebTest warnings regarding WSGI
warnings.filterwarnings('ignore', category=lint.WSGIWarning)


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


SETTINGS = appconfig('config:' + get_config_file_path())

# Scan sandglass time models to for registration
# before FIXTURE_ENV is initialized
models.scan_models('sandglass.time.models')

# Init fixture to database mappings environment.
# This registers all current Model definitions to
# be vailable for the fixtures.
FIXTURE_ENV = MODEL_REGISTRY
FIXTURE_ENV.update({
    'AdminUser': MODEL_REGISTRY['User'],
})

# Create the db-fixtures
FIXTURE = SQLAlchemyFixture(
    env=FIXTURE_ENV,
    style=NamedDataStyle(),
    engine=engine_from_config(SETTINGS, prefix='database.'),
)


def fixture(*datasets):
    """
    Test method decorator that sets up a fixture before test is run.

    Fixture data can be accessed during test as `fixture_data` attribute
    of the test instance.

    """
    def wrapper(func):
        @wraps(func)
        def call_func(data, self, *args, **kwargs):
            # Skip data argument when is not needed
            self.fixture_data = data
            try:
                return func(self, *args, **kwargs)
            finally:
                # Clear all tables to avoid conflict with used fixtures
                models.clear_tables()
                del self.fixture_data

        wrapper = FIXTURE.with_data(*datasets)
        return wrapper(call_func)

    return wrapper


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
                if inspect.isclass(value) and issubclass(value, BaseFixture):
                    # Save related fixtures as dictionaries
                    data[attr_name] = value.to_dict()
                else:
                    data[attr_name] = value

        return data


# API HTTP basic authorization token and key for admin test user
AUTH_TOKEN = "058bb38b25ddefa3f20537fd8762633dd2c3472f36f9b6628662624fffc7cbc2"
AUTH_KEY = "56f750326fe58c2266e864d4cd95c6ea2877ce9aa5da0b73ef57f2e8774433a4"


class AdminUserData(DataSet):
    """
    Fixture dataset with test admin user definitions.

    """
    class Admin(BaseFixture):
        first_name = u"Admin"
        last_name = u"User"
        email = u"admin@sandglass.net"
        password = "1234"
        token = AUTH_TOKEN
        key = AUTH_KEY
        salt = "a66a328e85e9d74da8dac441cb6f5578c530c70f"
        groups = [GroupData.Admins]


class BaseTestCase(unittest.TestCase):
    """
    Base class for all tests.

    """
    @classmethod
    def setUpClass(cls):
        cls.settings = SETTINGS
        super(BaseTestCase, cls).setUpClass()

    def setUp(self):
        # Disable logging during tests
        logging.disable(logging.CRITICAL)
        super(BaseTestCase, self).setUp()

    def tearDown(self):
        # Enable logging during tests
        logging.disable(logging.NOTSET)
        super(BaseTestCase, self).tearDown()

    def setup_default_data(self):
        from sandglass.time.install import DEFAULT_DATASETS

        # Add authorization data to defaults
        datasets = list(DEFAULT_DATASETS)
        datasets.append(AdminUserData)

        # Insert default data into database
        self.default_fixture_data = FIXTURE.data(*datasets)
        # self.default_fixture_data = FIXTURE.data(AdminUserData)
        self.default_fixture_data.setup()

    def teardown_default_data(self):
        # Remove all model object instances from loader session.
        # This is called here because the fixture teardown does
        # not expunge and because of that there are conflict
        # with model instances loaded in `setup_default_data`.
        self.default_fixture_data.loader.session.expunge_all()

        # Unload all datasets
        self.default_fixture_data.teardown()


class UnitTestCase(BaseTestCase):
    """
    Base class for unit tests.

    Unit tests are small tests that only test 1 thing at a time.

    Database/tables are created at the beginning of each tests and
    tables are dropped after each test finishes.

    """
    def setUp(self):
        super(UnitTestCase, self).setUp()
        # Initialize Pyramid testing environment support
        request = testing.DummyRequest()
        config = testing.setUp(settings=self.settings, request=request)
        config.include('sandglass.time.config')
        self.setup_default_data()

    def tearDown(self):
        # Clear all table data to avoid conflicts when using fixtures
        # and to start next test with a clean database
        models.clear_tables()
        self.teardown_default_data()
        # Cleanup Pyramid testing environment
        testing.tearDown()
        super(UnitTestCase, self).tearDown()


class IntegrationTestCase(UnitTestCase):
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
    require_authorization = False

    @classmethod
    def setUpClass(cls):
        super(FunctionalTestCase, cls).setUpClass()
        # Initialize Pyramid testing environment support
        request = testing.DummyRequest()
        cls.config = testing.setUp(settings=cls.settings, request=request)
        cls.config.include('sandglass.time.config')
        cls.wsgi_app = cls.config.make_wsgi_app()

    @classmethod
    def tearDownClass(cls):
        # Cleanup Pyramid testing environment
        testing.tearDown()
        super(FunctionalTestCase, cls).tearDownClass()

    def setUp(self):
        self.setup_default_data()
        self.app = TestApp(self.wsgi_app)
        super(FunctionalTestCase, self).setUp()

    def tearDown(self):
        self.teardown_default_data()
        # Clear all table data to start next test with a clean database
        models.clear_tables()
        super(FunctionalTestCase, self).tearDown()

    def get_authorization_header(self):
        """
        Get HTTP basic auth headers for current token and key.

        Returns a Dictionary.

        """
        header = {}
        auth_string = "{}:{}".format(AUTH_TOKEN, AUTH_KEY)
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
