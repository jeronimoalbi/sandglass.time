import os
import unittest

from paste.deploy.loadwsgi import appconfig
from pyramid import testing
from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker
from webtest import TestApp
from zope.sqlalchemy import ZopeTransactionExtension

# Fixture Stuffs
from fixture import SQLAlchemyFixture
from fixture.style import NamedDataStyle
from sandglass.time.tests.fixtures import UserData, ClientData, ProjectData
from sandglass.time import models
from sandglass.time.models import activity, client, project, tag, task, user


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
    env={'User': user.User,
          'Client': client.Client,
          'Project': project.Project,
          'Tag': tag.Tag,
          'Task': task.Task,
          'Activity': models.activity.Activity,
         }, 
    style=NamedDataStyle(),
    engine=engine_from_config(SETTINGS, prefix='database.'))


def fixture(*datasets):
    """
    Test method decorator that sets up a fixture before test is run.

    """
    def fixture_wrapper(func):
        wrapper = FIXTURE.with_data(*datasets)
        return wrapper(func)

    return fixture_wrapper


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
    def clear_database(cls):
        from sandglass.time.models import clear_tables
        clear_tables()

    @classmethod
    def setup_application(cls):
        request = testing.DummyRequest()
        # Initialize Pyramid testing environment support
        cls.config = testing.setUp(settings=cls.settings, request=request)
        cls.config.include('sandglass.time')

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


class FunctionalTestCase(BaseTestCase):

    """
    Base class for integration tests.

    This will integrate with the whole web framework and test
    the full stack of your application.

    Test WSGI application can be accesed as `self.app`.

    Database and tables are created before any test is run and
    tables are dropped when all tests are finished.

    """

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
        super(FunctionalTestCase, self).setUp()

    # def test_user_url_
    # def _action_create_model(self, model):
    #     url = model.get_member_url()
    #     response =

    def _create(self, path, content=None, status=200):
        create_response = self.app.post_json(path, content, status=status)
        created_id = create_response.json[0]['id']
        json = create_response.json

        return (created_id, json)
